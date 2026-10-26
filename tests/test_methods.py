"""Locked E1–E5 residuals vs public literature. No E6. Extraction is not gold."""

from __future__ import annotations

from evaluation.score import item_as_pred, load_all_gold_items, score_item
from evidencegraph.relations import relation_from_claims
from graph.store import load_document, to_jsonld
from tests.conftest import ITEMS


def _item(item_id: str) -> dict:
    return load_document(ITEMS / f"{item_id}.yaml")


def test_e1_qualifies_when_cohort_atlas_protocol_incomparable():
    """SciFact/AskChem polarity residual: I003 is Qualifies, not Contradicts."""
    item = _item("I003")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Qualifies"
    assert relation != "Contradicts"
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["relation_predicted"] == "Qualifies"


def test_e2_missing_code_is_unknown_not_assessed():
    """I004: missing artifacts are unknown_not_assessed, not a failed reproduction."""
    item = _item("I004")
    states = item["gold_claim"]["epistemic_states"]
    assert "unknown_not_assessed" in states
    assert "computationally_reproduced" not in states
    score = score_item(item, item_as_pred(item), arm="B6")
    assert score["false_reproduction"] is False


def test_e3_claim_method_run_without_asserting_execution():
    """PROV/RO-Crate optional. I004/I005 do not assert a WorkflowRun happened."""
    for item_id in ("I004", "I005"):
        item = _item(item_id)
        claim = item["gold_claim"]
        assert claim.get("method")
        assert claim.get("workflow_run") in {None, "unavailable"}
        assert "computationally_reproduced" not in claim["epistemic_states"]
        export = to_jsonld(claim)
        assert export["@context"]["prov"] == "http://www.w3.org/ns/prov#"
        assert export["eg:workflow_run"] in {None, "unavailable"}


def test_e4_primary_is_claim_source_span_scope():
    """ScholarQA/PaperQA2 residual: I001/I002 score (claim, source, span, scope)."""
    i001 = score_item(_item("I001"), item_as_pred(_item("I001")), arm="B6")
    assert i001["attribution_correct"] is True
    assert i001["relation_predicted"] == "Supports"
    i002 = score_item(_item("I002"), item_as_pred(_item("I002")), arm="B6")
    assert i002["attribution_correct"] is True
    assert i002["unsupported"] is True
    assert i002["relation_gold"] == "none"


def test_e5_construction_expert_entered_extraction_not_gold():
    """EVI owns the name. Construction: expert_entered; extraction_is_gold false."""
    items = load_all_gold_items()
    assert [i["item_id"] for i in items] == ["I001", "I002", "I003", "I004", "I005"]
    for item in items:
        cons = item["construction"]
        assert cons["origin"] == "expert_entered"
        assert cons["extraction_is_gold"] is False
        assert item["gold_claim"]["construction"]["extraction_is_gold"] is False
