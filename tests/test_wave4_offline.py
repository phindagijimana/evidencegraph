"""Wave 4 offline slice: network-off ingest, JSON-LD, fixture DOIs only.

EVI owns the name. Extraction is not gold. No React. Not a paper-agent.
Never stores restricted full text.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from evaluation.score import item_as_pred, score_item
from evidencegraph.agent import TOOLS, call_tool
from evidencegraph.relations import relation_from_claims
from graph.store import ClaimStore, load_document, normalize_claim, to_jsonld
from ingest.resolve import (
    LicenseRefused,
    NetworkScrapeRefused,
    ResolutionError,
    resolve,
)
from tests.conftest import ITEMS, PACKAGE_ROOT

OA_DOI = "10.9999/eg.fixture.surgical-hs"
RESTRICTED_DOI = "10.9999/restricted-mock"
UNKNOWN_DOI = "10.1234/not-in-manifest"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"
WAVE4_ITEMS = ("F004", "F005")
WAVE4_PAPERS = ("P-HS-SURGICAL-OPP-007", "P-HS-LOGGED-RUN-008")
CORPUS = PACKAGE_ROOT / "corpus"


def _boom(*_args, **_kwargs):
    raise AssertionError("HTTP must not be called")


def test_ingest_network_off_by_default():
    with pytest.raises(ResolutionError, match="network is off"):
        resolve(UNKNOWN_DOI, license_check=True)


def test_network_without_local_oa_refuses_scrape(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.europepmc._http_get", _boom)
    with pytest.raises(NetworkScrapeRefused, match="refuse scrape"):
        resolve(UNKNOWN_DOI, license_check=True, network=True)


def test_network_with_local_oa_uses_manifest_and_does_not_scrape(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.europepmc._http_get", _boom)
    record = resolve(OA_DOI, license_check=True, network=True, store_dir=tmp_path)
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["ingest"]["scrape"] is False
    assert record["ingest"]["network"] == "requested_local_only"
    assert record["ingest"]["resolver"] == "local_manifest"
    for path in tmp_path.rglob("*"):
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert SECRET not in body
            assert "<article" not in body


def test_network_with_local_restricted_record_refuses_and_does_not_scrape(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.europepmc._http_get", _boom)
    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            RESTRICTED_DOI,
            license_check=True,
            network=True,
            store_dir=tmp_path,
            metadata={
                "doi": RESTRICTED_DOI,
                "license": "all-rights-reserved",
                "is_oa": False,
                "full_text": SECRET,
            },
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert SECRET not in path.read_text(encoding="utf-8", errors="ignore")


def test_cli_network_without_local_oa_exits_nonzero():
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
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "refuse scrape" in proc.stderr


def test_cli_network_with_local_oa_does_not_store_full_text(tmp_path):
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
    for path in tmp_path.rglob("*"):
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert "full_text: null" in body or '"full_text"' not in body or payload["full_text"] is None
            assert SECRET not in body
            assert "<article" not in body


def test_agent_network_without_local_oa_is_scrape_refused():
    refused = call_tool("ingest", {"doi": UNKNOWN_DOI, "network": True})
    assert refused["reason"] == "scrape_refused"
    assert {tool["name"] for tool in TOOLS} == {"load", "ingest"}


def test_cli_export_jsonld_on_wave4_fixture():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "export",
            "--jsonld",
            "--item",
            str(ITEMS / "F004.yaml"),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    first = payload[0] if isinstance(payload, list) else payload
    assert first["@type"] == "eg:Claim"
    assert first["eg:claim_id"] == "C-F004-A"
    assert first["eg:origin"] == "expert_entered"
    assert first["eg:extraction_is_gold"] is False
    assert first["eg:relation"] == "Contradicts"
    assert first["@context"]["prov"] == "http://www.w3.org/ns/prov#"


def test_jsonld_marks_machine_extracted_as_not_gold():
    item = load_document(ITEMS / "I001.yaml")
    claim = dict(item["gold_claim"])
    claim["construction"] = {"origin": "machine_extracted", "extraction_is_gold": True}
    stored = normalize_claim(claim)
    assert stored["construction"]["origin"] == "machine_extracted"
    assert stored["construction"]["extraction_is_gold"] is False
    export = to_jsonld(stored)
    assert export["eg:origin"] == "machine_extracted"
    assert export["eg:extraction_is_gold"] is False


def test_wave4_fixture_papers_are_not_published_dois():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    papers = {p["paper_id"]: p for p in manifest["papers"]}
    for paper_id in WAVE4_PAPERS:
        paper = papers[paper_id]
        assert paper["fixture"] is True
        assert paper["not_a_published_doi"] is True
        assert paper["origin"] == "expert_entered"
        assert paper["extraction_is_gold"] is False
        assert str(paper["doi"]).startswith("10.9999/eg.fixture.")
        assert paper["full_text_stored"] is False
        source = PACKAGE_ROOT / paper["spans_path"]
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
        assert data["fixture"] is True
        assert data["not_a_published_doi"] is True
        assert data["extraction_is_gold"] is False


def test_wave4_items_expert_entered_not_gold():
    for item_id in WAVE4_ITEMS:
        item = load_document(ITEMS / f"{item_id}.yaml")
        assert item["fixture"] is True
        assert item["not_a_published_doi"] is True
        assert item["construction"]["origin"] == "expert_entered"
        assert item["construction"]["extraction_is_gold"] is False
        assert item["gold_claim"]["construction"]["extraction_is_gold"] is False


def test_f004_same_protocol_opposite_direction_is_contradicts():
    item = load_document(ITEMS / "F004.yaml")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Contradicts"
    assert relation != "Qualifies"
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["relation_predicted"] == "Contradicts"
    assert score["construction"]["extraction_is_gold"] is False


def test_f005_logged_run_coexists_with_reported(tmp_path):
    item = load_document(ITEMS / "F005.yaml")
    claim = item["gold_claim"]
    assert "reported" in claim["epistemic_states"]
    assert "computationally_reproduced" in claim["epistemic_states"]
    stored = ClaimStore(tmp_path).put(claim)
    assert "reported" in stored["epistemic_states"]
    assert "computationally_reproduced" in stored["epistemic_states"]
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["false_reproduction"] is False
    assert score["construction"]["extraction_is_gold"] is False


def test_no_restricted_full_text_stored_in_corpus():
    forbidden = (
        SECRET,
        "<article",
        "<full-text",
        "fullTextXml:",
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
            assert data.get("full_text_stored", False) is False


def test_evi_owns_the_name_and_no_react_or_paper_agent():
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    assert "EVI already owns the name" in readme
    assert "we introduce evidence graphs" not in readme.lower()
    assert "Not a paper-agent" in readme
    assert not list(PACKAGE_ROOT.rglob("*.tsx"))
    assert not (PACKAGE_ROOT / "package.json").exists()
    assert {tool["name"] for tool in TOOLS} == {"load", "ingest"}
