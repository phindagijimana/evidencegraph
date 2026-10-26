"""Wave 5 production slice: optional Crossref/Europe PMC, metadata only.

Network off by default. Extraction is not gold. EVI owns the name. No React.
Never stores restricted full text or Crossref abstracts.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
import yaml

from extraction.origin import tag_machine_extracted
from graph.store import normalize_claim, to_jsonld
from ingest.crossref import build_works_url
from ingest.resolve import (
    LicenseRefused,
    NetworkScrapeRefused,
    ResolutionError,
    resolve,
)
from tests.conftest import EXAMPLE_CLAIM, PACKAGE_ROOT

OA_DOI = "10.9999/eg.fixture.surgical-hs"
REAL_OA_DOI = "10.1038/sdata.2016.44"
UNKNOWN_DOI = "10.1234/not-in-manifest"
RESTRICTED_DOI = "10.9999/restricted-mock"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"
ABSTRACT = "MUST NOT BE STORED CROSSREF ABSTRACT"
BIDS_ABSTRACT_MARKERS = (
    "defined modern neuroimaging",
    "To solve this problem, we have developed the Brain Imaging Data Structure",
    "Despite the fact that MRI is routinely used",
)
CORPUS = PACKAGE_ROOT / "corpus"


def _boom(*_args, **_kwargs):
    raise AssertionError("HTTP must not be called")


def _works(message: dict) -> str:
    return json.dumps({"status": "ok", "message-type": "work", "message": message})


def test_crossref_network_off_by_default(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(ResolutionError, match="network is off"):
        resolve(UNKNOWN_DOI, license_check=True, source="crossref")


def test_network_without_local_oa_refuses_even_with_crossref_source(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(NetworkScrapeRefused, match="refuse scrape"):
        resolve(UNKNOWN_DOI, license_check=True, network=True, source="crossref")


def test_network_with_local_oa_crossref_stores_metadata_only(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    record = resolve(
        OA_DOI,
        license_check=True,
        network=True,
        source="crossref",
        store_dir=tmp_path,
    )
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["abstract"] is None
    assert record["full_text_stored"] is False
    assert record["ingest"]["scrape"] is False
    assert record["ingest"]["network"] == "requested_local_only"
    assert record["ingest"]["optional_client"] == "crossref"
    assert record["ingest"]["client_url"] == build_works_url(OA_DOI)
    for path in tmp_path.rglob("*"):
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert SECRET not in body
            assert ABSTRACT not in body
            assert "<article" not in body


def test_network_with_local_oa_mocked_crossref_strips_abstract(tmp_path):
    def opener(url: str) -> str:
        assert "api.crossref.org/works" in url
        return _works(
            {
                "DOI": OA_DOI,
                "title": ["Fixture OA"],
                "license": [{"URL": "https://creativecommons.org/licenses/by/4.0"}],
                "abstract": ABSTRACT,
            }
        )

    record = resolve(
        OA_DOI,
        license_check=True,
        network=True,
        source="crossref",
        opener=opener,
        store_dir=tmp_path,
    )
    assert record["full_text"] is None
    assert record["abstract"] is None
    assert record["ingest"]["resolver"] == "local_manifest+crossref"
    written = list(tmp_path.glob("*.meta.yaml"))
    assert written
    text = written[0].read_text(encoding="utf-8")
    assert ABSTRACT not in text


def test_network_with_local_restricted_does_not_call_crossref(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            RESTRICTED_DOI,
            license_check=True,
            network=True,
            source="crossref",
            store_dir=tmp_path,
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert SECRET not in path.read_text(encoding="utf-8", errors="ignore")


def test_cli_network_source_crossref_on_local_oa(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "--store",
            str(tmp_path),
            "ingest",
            "--doi",
            OA_DOI,
            "--license-check",
            "--network",
            "--source",
            "crossref",
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["full_text"] is None
    assert payload["ingest"]["scrape"] is False
    assert payload["ingest"]["optional_client"] == "crossref"


def test_cli_network_source_crossref_without_local_oa_exits_nonzero():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "ingest",
            "--doi",
            UNKNOWN_DOI,
            "--license-check",
            "--network",
            "--source",
            "crossref",
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "refuse scrape" in proc.stderr


def test_resolved_real_oa_paper_records_license_not_text():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    papers = {p["paper_id"]: p for p in manifest["papers"]}
    paper = papers["P-OA-BIDS-SDATA-2016"]
    assert paper["doi"] == REAL_OA_DOI
    assert paper["fixture"] is False
    assert paper["not_a_published_doi"] is False
    assert paper["license"] == "CC-BY-4.0"
    assert paper["resolved_via"] == "crossref"
    assert paper["full_text_stored"] is False
    assert paper["extraction_is_gold"] is False
    assert paper["spans_path"] is None
    assert paper["crossref"]["license_url"] == "https://creativecommons.org/licenses/by/4.0"
    recorded = (
        PACKAGE_ROOT / "corpus" / "pilot" / "recorded" / "10.1038_sdata.2016.44.meta.yaml"
    )
    data = yaml.safe_load(recorded.read_text(encoding="utf-8"))
    assert data["full_text"] is None
    assert data["abstract"] is None
    assert data["full_text_stored"] is False


def test_network_on_real_oa_record_stores_metadata_only(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    record = resolve(
        REAL_OA_DOI,
        license_check=True,
        network=True,
        source="crossref",
        store_dir=tmp_path,
    )
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["abstract"] is None
    text = (tmp_path / "10.1038_sdata.2016.44.meta.yaml").read_text(encoding="utf-8")
    for marker in BIDS_ABSTRACT_MARKERS:
        assert marker not in text


def test_extraction_is_never_gold():
    claim = yaml.safe_load(EXAMPLE_CLAIM.read_text(encoding="utf-8"))
    tagged = tag_machine_extracted(
        {**claim, "construction": {"origin": "expert_entered", "extraction_is_gold": True}}
    )
    assert tagged["construction"]["origin"] == "machine_extracted"
    assert tagged["construction"]["extraction_is_gold"] is False
    stored = normalize_claim(tagged)
    assert stored["construction"]["extraction_is_gold"] is False
    export = to_jsonld(stored)
    assert export["eg:origin"] == "machine_extracted"
    assert export["eg:extraction_is_gold"] is False


def test_no_invented_journal_dois_without_recorded_license():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    for paper in manifest["papers"]:
        doi = str(paper.get("doi") or "")
        if paper.get("fixture"):
            assert doi.startswith("10.9999/"), doi
            continue
        assert paper.get("license")
        assert paper.get("resolved_via") in {"crossref", "europepmc"}
        assert paper.get("full_text_stored") is False
        assert (paper.get("crossref") or {}).get("license_url")


def test_no_restricted_or_abstract_text_in_corpus():
    forbidden = (
        SECRET,
        ABSTRACT,
        "<article",
        "<full-text",
        "fullTextXml:",
        *BIDS_ABSTRACT_MARKERS,
    )
    for path in CORPUS.rglob("*"):
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            assert token not in body, f"{token!r} in {path}"
        data = yaml.safe_load(body)
        if isinstance(data, dict):
            assert data.get("full_text") in (None, "")
            assert data.get("abstract") in (None, "", False) or "abstract" not in data
            assert data.get("full_text_stored", False) is False


def test_evi_owns_the_name_and_no_react():
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    assert "EVI already owns the name" in readme
    assert "we introduce evidence graphs" not in readme.lower()
    assert not list(PACKAGE_ROOT.rglob("*.tsx"))
    assert not (PACKAGE_ROOT / "package.json").exists()
