"""Same five gold items through B4 polarity and scoped EvidenceGraph score.

Behavioral assertions only. No fabricated results. Extraction is not gold.
"""

from __future__ import annotations

import pytest

from baselines.polarity import polarity_from_item
from evaluation.score import item_as_pred, load_all_gold_items, score_item
from graph.store import load_document
from ingest.resolve import LicenseRefused, resolve
from tests.conftest import ITEMS

RESTRICTED_DOI = "10.9999/restricted-mock"


def _item(item_id: str) -> dict:
    return load_document(ITEMS / f"{item_id}.yaml")


def _b6(item_id: str, pred: dict | None = None) -> dict:
    item = _item(item_id)
    return score_item(item, pred if pred is not None else item_as_pred(item), arm="B6")


def test_i001_finding_polarity_supports_eg_attribution():
    item = _item("I001")
    assert polarity_from_item(item) == "Supports"
    score = _b6("I001")
    assert score["relation_predicted"] == "Supports"
    assert score["attribution_correct"] is True
    assert score["construction"]["extraction_is_gold"] is False


def test_i002_background_polarity_none_eg_unsupported():
    item = _item("I002")
    assert polarity_from_item(item) == "none"
    score = _b6("I002")
    assert score["relation_gold"] == "none"
    assert score["relation_predicted"] == "none"
    assert score["unsupported"] is True


def test_i003_polarity_may_contradict_eg_qualifies_not_contradicts():
    item = _item("I003")
    b4 = polarity_from_item(item)
    assert b4 in {"Contradicts", "Supports"}
    score = _b6("I003")
    assert score["relation_predicted"] == "Qualifies"
    assert score["relation_predicted"] != "Contradicts"
    assert score["relation_gold"] == "Qualifies"


def test_i004_eg_unknown_not_assessed():
    score = _b6("I004")
    assert "unknown_not_assessed" in score["epistemic_states_gold"]
    assert "computationally_reproduced" not in score["epistemic_states_gold"]
    assert score["false_reproduction"] is False


def test_i005_eg_false_reproduction_when_system_asserts_run():
    item = _item("I005")
    pred = item_as_pred(item)
    pred["epistemic_states"] = ["reported", "computationally_reproduced"]
    pred["asserts_reproduced"] = True
    score = score_item(item, pred, arm="B6")
    assert score["false_reproduction"] is True
    assert "unknown_not_assessed" in item["gold_claim"]["epistemic_states"]


def test_license_refuse_holds_on_mocked_non_oa_doi():
    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(RESTRICTED_DOI, license_check=True)


def test_same_five_items_through_polarity_and_scoped_score():
    items = load_all_gold_items()
    assert [i["item_id"] for i in items] == ["I001", "I002", "I003", "I004", "I005"]
    for item in items:
        b4 = polarity_from_item(item)
        assert b4 in {"Supports", "Contradicts", "none"}
        score = score_item(item, item_as_pred(item), arm="B6")
        assert score["item_id"] == item["item_id"]
        assert score["construction"]["origin"] == "expert_entered"
        assert score["construction"]["extraction_is_gold"] is False
