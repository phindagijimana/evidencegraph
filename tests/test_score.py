"""E4/E5: five gold items load and score. Extraction is not gold."""

from __future__ import annotations

from copy import deepcopy

from evaluation.score import item_as_pred, load_all_gold_items, score_item
from graph.query import query_claim
from graph.store import ClaimStore, load_document, to_jsonld
from tests.conftest import EXAMPLE_CLAIM, ITEMS, PACKAGE_ROOT


def test_example_claim_loads(tmp_path):
    store = ClaimStore(tmp_path)
    loaded = store.load_path(EXAMPLE_CLAIM)
    assert loaded[0]["claim_id"] == "C001"
    assert loaded[0]["construction"]["extraction_is_gold"] is False


def test_five_gold_items_load_and_score_offline(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    store = ClaimStore(tmp_path)
    items = load_all_gold_items()
    assert len(items) == 5
    for item in items:
        store.load_path(ITEMS / f"{item['item_id']}.yaml")
        pred = item_as_pred(item)
        score = score_item(item, pred, arm="B6")
        assert score["item_id"] == item["item_id"]
        assert score["attribution_correct"] is True
        assert score["construction"]["extraction_is_gold"] is False
        assert score["construction"]["origin"] == "expert_entered"


def test_i001_supports_attribution():
    item = load_document(ITEMS / "I001.yaml")
    score = score_item(item, item_as_pred(item))
    assert score["relation_gold"] == "Supports"
    assert score["relation_predicted"] == "Supports"
    assert score["attribution_correct"] is True
    assert score["unsupported"] is False


def test_i002_background_span_is_unsupported():
    item = load_document(ITEMS / "I002.yaml")
    score = score_item(item, item_as_pred(item))
    assert score["relation_gold"] == "none"
    assert score["unsupported"] is True
    assert score["attribution_correct"] is True


def test_i003_qualifies_not_contradicts():
    item = load_document(ITEMS / "I003.yaml")
    score = score_item(item, item_as_pred(item))
    assert score["relation_gold"] == "Qualifies"
    assert score["relation_predicted"] == "Qualifies"
    assert score["family"] == "apparent_contradiction"


def test_i004_unknown_not_assessed():
    item = load_document(ITEMS / "I004.yaml")
    score = score_item(item, item_as_pred(item))
    assert "unknown_not_assessed" in score["epistemic_states_gold"]
    assert "computationally_reproduced" not in score["epistemic_states_gold"]
    assert score["false_reproduction"] is False


def test_i005_false_reproduction_when_system_asserts_run():
    item = load_document(ITEMS / "I005.yaml")
    pred = item_as_pred(item)
    pred["epistemic_states"] = [
        "reported",
        "computationally_reproduced",
    ]
    pred["asserts_reproduced"] = True
    score = score_item(item, pred)
    assert score["false_reproduction"] is True
    assert "unknown_not_assessed" in item["gold_claim"]["epistemic_states"]


def test_wrong_scope_fails_attribution():
    item = load_document(ITEMS / "I001.yaml")
    pred = item_as_pred(item)
    pred["claim"]["scope"] = deepcopy(pred["claim"]["scope"])
    pred["claim"]["scope"]["population"] = "community epilepsy cohort"
    score = score_item(item, pred)
    assert score["scope_correct"] is False
    assert score["attribution_correct"] is False


def test_wrong_span_fails_attribution():
    item = load_document(ITEMS / "I001.yaml")
    pred = item_as_pred(item)
    pred["claim"]["evidence_span"] = deepcopy(pred["claim"]["evidence_span"])
    pred["claim"]["evidence_span"]["paragraph_id"] = "background-p1"
    score = score_item(item, pred)
    assert score["span_correct"] is False
    assert score["attribution_correct"] is False


def test_export_marks_expert_not_extraction(tmp_path):
    item = load_document(ITEMS / "I001.yaml")
    store = ClaimStore(tmp_path)
    stored = store.put(item["gold_claim"])
    export = to_jsonld(stored)
    assert export["eg:origin"] == "expert_entered"
    assert export["eg:extraction_is_gold"] is False
    queried = query_claim(store, "C-I001", show_scope=True)
    assert queried is not None
    assert queried["scope"]["method_identity"] == "FreeSurfer 6.0"
    assert queried["construction"]["extraction_is_gold"] is False


def test_no_machine_extracted_gold_in_v0():
    for item in load_all_gold_items():
        assert item["construction"]["origin"] == "expert_entered"
        assert item["construction"]["extraction_is_gold"] is False
        assert item["gold_claim"]["construction"]["extraction_is_gold"] is False


def test_schema_and_handbook_exist():
    assert (PACKAGE_ROOT / "annotations" / "handbook.md").is_file()
    assert (PACKAGE_ROOT / "schema" / "score.schema.json").is_file()
    assert (PACKAGE_ROOT / "docs" / "EvidenceGraph_Literature_Map.md").is_file()
