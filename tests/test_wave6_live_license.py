"""Wave 6: live metadata-only license check; S0 accession; more OA records.

Live license check refuses non-OA. Qualifies ≠ Contradicts. EVI owns the name.
Never stores restricted full text or abstracts. No invented DOIs.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
import yaml

from evaluation.score import item_as_pred, score_item
from evidencegraph.relations import relation_from_claims
from graph.store import load_document
from ingest.crossref import LIVE_ENV, build_works_url
from ingest.resolve import LicenseRefused, NetworkScrapeRefused, ResolutionError, resolve
from tests.conftest import ITEMS, PACKAGE_ROOT

UNKNOWN_DOI = "10.1234/not-in-manifest"
RESTRICTED_DOI = "10.9999/restricted-mock"
REAL_OA_DOI = "10.1038/sdata.2016.44"
BIDS_APPS_DOI = "10.1371/journal.pcbi.1005209"
OPENNEURO_DOI = "10.7554/eLife.71774"
S0_DATASET_DOI = "10.18112/openneuro.ds000003.v1.0.0"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"
ABSTRACT = "MUST NOT BE STORED CROSSREF ABSTRACT"
BIDS_ABSTRACT_MARKERS = (
    "defined modern neuroimaging",
    "To solve this problem, we have developed the Brain Imaging Data Structure",
    "Despite the fact that MRI is routinely used",
)
CORPUS = PACKAGE_ROOT / "corpus"
NEW_OA = {
    "P-OA-BIDSAPPS-PCB-2017": BIDS_APPS_DOI,
    "P-OA-OPENNEURO-ELIFE-2021": OPENNEURO_DOI,
}


def _works(message: dict) -> str:
    return json.dumps({"status": "ok", "message-type": "work", "message": message})


def _boom(*_args, **_kwargs):
    raise AssertionError("HTTP must not be called")


def test_live_license_refuses_mocked_non_oa_and_does_not_store_text(tmp_path):
    leaked = tmp_path / "leak.txt"
    leaked.write_text(SECRET, encoding="utf-8")

    def opener(url: str) -> str:
        assert "api.crossref.org/works" in url
        return _works(
            {
                "DOI": UNKNOWN_DOI,
                "title": ["Mocked non-OA"],
                "license": [{"URL": "https://www.elsevier.com/tdm/userlicense/1.0/"}],
                "abstract": SECRET,
            }
        )

    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            UNKNOWN_DOI,
            license_check=True,
            live_license=True,
            source="crossref",
            opener=opener,
            store_dir=tmp_path,
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert SECRET not in path.read_text(encoding="utf-8", errors="ignore")


def test_live_license_refuses_tdm_only_license(tmp_path):
    def opener(url: str) -> str:
        return _works(
            {
                "DOI": UNKNOWN_DOI,
                "title": ["TDM-only work"],
                "license": [
                    {
                        "URL": (
                            "https://www.springernature.com/gp/researchers/"
                            "text-and-data-mining"
                        )
                    }
                ],
                "abstract": ABSTRACT,
            }
        )

    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            UNKNOWN_DOI,
            license_check=True,
            live_license=True,
            source="crossref",
            opener=opener,
            store_dir=tmp_path,
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert ABSTRACT not in path.read_text(encoding="utf-8", errors="ignore")


def test_live_license_oa_stores_metadata_only(tmp_path):
    def opener(url: str) -> str:
        assert "api.crossref.org/works" in url
        return _works(
            {
                "DOI": UNKNOWN_DOI,
                "title": ["Fixture OA via live license"],
                "license": [{"URL": "https://creativecommons.org/licenses/by/4.0"}],
                "publisher": "Fixture Press",
                "abstract": ABSTRACT,
            }
        )

    record = resolve(
        UNKNOWN_DOI,
        license_check=True,
        live_license=True,
        source="crossref",
        opener=opener,
        store_dir=tmp_path,
    )
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["abstract"] is None
    assert record["full_text_stored"] is False
    assert record["ingest"]["scrape"] is False
    assert record["ingest"]["network"] == "live_license"
    assert record["ingest"]["resolver"] == "crossref"
    assert record["ingest"]["client_url"] == build_works_url(UNKNOWN_DOI)
    written = list(tmp_path.glob("*.meta.yaml"))
    assert written
    text = written[0].read_text(encoding="utf-8")
    assert ABSTRACT not in text
    assert SECRET not in text


def test_network_without_live_license_still_refuses_scrape(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(NetworkScrapeRefused, match="refuse scrape"):
        resolve(UNKNOWN_DOI, license_check=True, network=True, source="crossref")


def test_live_license_off_unknown_doi_does_not_hit_network(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(ResolutionError, match="network is off"):
        resolve(UNKNOWN_DOI, license_check=True)


def test_live_license_without_opener_or_gate_stays_offline(monkeypatch):
    monkeypatch.delenv(LIVE_ENV, raising=False)
    monkeypatch.setattr("urllib.request.urlopen", _boom)
    monkeypatch.setattr("ingest.crossref._http_get", _boom)
    with pytest.raises(ResolutionError, match="live license check network is off"):
        resolve(
            UNKNOWN_DOI,
            license_check=True,
            live_license=True,
            source="crossref",
            live=False,
        )


def test_cli_live_license_on_local_restricted_exits_nonzero():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "ingest",
            "--doi",
            RESTRICTED_DOI,
            "--license-check",
            "--live-license",
            "--source",
            "crossref",
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "not redistributable" in proc.stderr


def test_cli_network_without_live_license_still_refuses_unknown():
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


def test_new_oa_records_are_real_licenses_without_full_text():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    papers = {p["paper_id"]: p for p in manifest["papers"]}
    for paper_id, doi in NEW_OA.items():
        paper = papers[paper_id]
        assert paper["doi"] == doi
        assert paper["fixture"] is False
        assert paper["not_a_published_doi"] is False
        assert paper["license"] == "CC-BY-4.0"
        assert paper["resolved_via"] == "crossref"
        assert paper["full_text_stored"] is False
        assert paper["extraction_is_gold"] is False
        assert paper["spans_path"] is None
        assert paper["crossref"]["license_url"]
        recorded = (
            PACKAGE_ROOT
            / "corpus"
            / "pilot"
            / "recorded"
            / f"{doi.replace('/', '_')}.meta.yaml"
        )
        data = yaml.safe_load(recorded.read_text(encoding="utf-8"))
        assert data["doi"] == doi
        assert data["full_text"] is None
        assert data["abstract"] is None
        assert data["full_text_stored"] is False
        body = recorded.read_text(encoding="utf-8")
        for marker in BIDS_ABSTRACT_MARKERS:
            assert marker not in body


def test_gorgolewski_2016_still_recorded_and_points_at_s0():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    papers = {p["paper_id"]: p for p in manifest["papers"]}
    paper = papers["P-OA-BIDS-SDATA-2016"]
    assert paper["doi"] == REAL_OA_DOI
    assert paper["license"] == "CC-BY-4.0"
    assert "ds000003" in paper["related_accessions"]
    recorded = (
        PACKAGE_ROOT / "corpus" / "pilot" / "recorded" / "10.1038_sdata.2016.44.meta.yaml"
    )
    data = yaml.safe_load(recorded.read_text(encoding="utf-8"))
    assert data["related_accessions"] == ["ds000003"]
    assert data["full_text"] is None
    assert data["abstract"] is None


def test_s0_accession_is_recorded_without_nifti():
    manifest = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml").read_text(encoding="utf-8")
    )
    accessions = {a["accession"]: a for a in manifest["accessions"]}
    acc = accessions["ds000003"]
    assert acc["doi"] == S0_DATASET_DOI
    assert acc["not_a_journal_article"] is True
    assert acc["bytes_in_git"] is False
    assert acc["nifti_in_this_folder"] is False
    assert acc["full_text_stored"] is False
    assert acc["extraction_is_gold"] is False
    assert acc["external_path"] == "shared/data/external/ds000003"
    assert "P-OA-BIDS-SDATA-2016" in acc["related_papers"]
    record = yaml.safe_load(
        (PACKAGE_ROOT / "corpus" / "pilot" / "accessions" / "ds000003.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert record["accession"] == "ds000003"
    assert record["full_text"] is None
    assert record["abstract"] is None
    niftis = list(PACKAGE_ROOT.rglob("*.nii")) + list(PACKAGE_ROOT.rglob("*.nii.gz"))
    assert niftis == []


def test_i003_still_qualifies_not_contradicts():
    item = load_document(ITEMS / "I003.yaml")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Qualifies"
    assert relation != "Contradicts"
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["relation_predicted"] == "Qualifies"


def test_evi_owns_the_name_and_pytest_workflow_kept():
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    assert "EVI already owns the name" in readme
    assert "we introduce evidence graphs" not in readme.lower()
    workflow = PACKAGE_ROOT / ".github" / "workflows" / "pytest.yml"
    assert workflow.is_file()
    text = workflow.read_text(encoding="utf-8")
    assert "OPENAI_API_KEY" in text
    assert "nii" in text
