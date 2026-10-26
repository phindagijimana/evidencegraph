"""Wave 3 fixtures, JSON-LD/BM25 CLI, I003 still Qualifies. No published DOIs."""

from __future__ import annotations

import json
import subprocess
import sys

import yaml

from evaluation.score import item_as_pred, load_all_gold_items, score_item
from evidencegraph.relations import relation_from_claims
from graph.store import load_document, to_jsonld
from ingest.resolve import load_manifest
from tests.conftest import ITEMS, PACKAGE_ROOT

EXTRA_ITEM_IDS = ("F001", "F002", "F003")
EXTRA_PAPER_IDS = (
    "P-HS-ATLAS-004",
    "P-HS-FIELDSTRENGTH-005",
    "P-HS-CONNECTOME-006",
)


def test_wave1_gold_set_unchanged():
    items = load_all_gold_items()
    assert [i["item_id"] for i in items] == ["I001", "I002", "I003", "I004", "I005"]


def test_i003_still_qualifies_not_contradicts():
    item = load_document(ITEMS / "I003.yaml")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Qualifies"
    assert relation != "Contradicts"
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["relation_predicted"] == "Qualifies"
    assert score["relation_gold"] == "Qualifies"


def test_additional_fixture_papers_are_not_published_dois():
    manifest = load_manifest()
    papers = {p["paper_id"]: p for p in manifest["papers"]}
    for paper_id in EXTRA_PAPER_IDS:
        paper = papers[paper_id]
        assert paper["fixture"] is True
        assert paper["not_a_published_doi"] is True
        assert paper["origin"] == "expert_entered"
        assert paper["extraction_is_gold"] is False
        assert str(paper["doi"]).startswith("10.9999/eg.fixture.")
        assert paper["full_text_stored"] is False
        source = PACKAGE_ROOT / paper["spans_path"]
        assert source.is_file()
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
        assert data["fixture"] is True
        assert data["not_a_published_doi"] is True
        assert data["extraction_is_gold"] is False


def test_no_invented_published_dois_in_manifest():
    for paper in load_manifest()["papers"]:
        doi = str(paper.get("doi") or "")
        assert doi.startswith("10.9999/"), doi
        assert paper.get("fixture") is True
        assert paper.get("not_a_published_doi") is True


def test_additional_items_expert_entered_not_gold():
    for item_id in EXTRA_ITEM_IDS:
        item = load_document(ITEMS / f"{item_id}.yaml")
        assert item["fixture"] is True
        assert item["not_a_published_doi"] is True
        assert item["construction"]["origin"] == "expert_entered"
        assert item["construction"]["extraction_is_gold"] is False
        assert item["gold_claim"]["construction"]["extraction_is_gold"] is False


def test_f001_atlas_mismatch_is_qualifies():
    item = load_document(ITEMS / "F001.yaml")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Qualifies"
    assert relation != "Contradicts"


def test_f002_transfer_without_scope_is_unknown_scope():
    item = load_document(ITEMS / "F002.yaml")
    assert item["abstain"] is True
    assert item["gold_claim"]["relation"] == "unknown_scope"


def test_cli_export_jsonld_on_gold_item():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "export",
            "--jsonld",
            "--item",
            str(ITEMS / "I001.yaml"),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["@type"] == "eg:Claim"
    assert payload["eg:claim_id"] == "C-I001"
    assert payload["eg:origin"] == "expert_entered"
    assert payload["eg:extraction_is_gold"] is False
    assert payload["@context"]["prov"] == "http://www.w3.org/ns/prov#"
    expected = to_jsonld(load_document(ITEMS / "I001.yaml")["gold_claim"])
    assert payload["eg:relation"] == expected["eg:relation"]


def test_cli_retrieve_bm25_on_fixture_corpus():
    query = "FreeSurfer 6.0 pathology-defined hippocampal sclerosis surgical cohort"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "retrieve",
            "--bm25",
            "--query",
            query,
            "--k",
            "20",
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["arm"] == "B0"
    hits = payload["hits"]
    assert hits
    assert hits[0]["paper_id"] == "P-HS-SURGICAL-001"
    assert hits[0]["paragraph_id"] == "results-p2"
    by_id = {hit["doc_id"]: hit for hit in hits}
    assert "P-HS-SURGICAL-001#background-p1" in by_id
    assert (
        by_id["P-HS-SURGICAL-001#results-p2"]["score"]
        > by_id["P-HS-SURGICAL-001#background-p1"]["score"]
    )


def test_cli_export_requires_jsonld():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "export",
            "--item",
            str(ITEMS / "I001.yaml"),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
