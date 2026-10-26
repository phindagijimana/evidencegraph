"""E1: Qualifies vs Contradicts on scope mismatch."""

from __future__ import annotations

from copy import deepcopy

from evaluation.score import load_all_gold_items
from evidencegraph.relations import decide_relation, relation_from_claims
from graph.store import load_document
from tests.conftest import ITEMS


def _scope(**overrides):
    base = {
        "population": "surgical epilepsy cohort",
        "acquisition": "3T research MRI",
        "method_identity": "FreeSurfer 6.0",
        "comparator": "pathology-defined hippocampal sclerosis",
        "timepoint": "preoperative",
        "outcome_definition": "hippocampal asymmetry associated with HS",
    }
    base.update(overrides)
    return base


def test_scope_mismatch_is_qualifies_not_contradicts():
    relation = decide_relation(
        claim_family_match=True,
        scope_a=_scope(),
        scope_b=_scope(
            population="community epilepsy cohort",
            acquisition="1.5T community MRI",
            method_identity="ASHS",
            comparator="imaging-defined hippocampal sclerosis",
        ),
        direction_a="associated",
        direction_b="not_associated",
        span_licenses=True,
    )
    assert relation == "Qualifies"
    assert relation != "Contradicts"


def test_comparable_opposite_direction_is_contradicts():
    relation = decide_relation(
        claim_family_match=True,
        scope_a=_scope(),
        scope_b=_scope(),
        direction_a="associated",
        direction_b="not_associated",
        span_licenses=True,
    )
    assert relation == "Contradicts"


def test_comparable_same_direction_is_supports():
    relation = decide_relation(
        claim_family_match=True,
        scope_a=_scope(),
        scope_b=_scope(),
        direction_a="associated",
        direction_b="associated",
        span_licenses=True,
    )
    assert relation == "Supports"


def test_insufficient_scope_is_unknown_scope():
    unknown = {
        "population": "unknown",
        "acquisition": "unknown",
        "method_identity": "unknown",
        "comparator": "unknown",
        "timepoint": "unknown",
        "outcome_definition": "unknown",
    }
    relation = decide_relation(
        claim_family_match=True,
        scope_a=unknown,
        scope_b=unknown,
        direction_a="associated",
        direction_b="not_associated",
        span_licenses=True,
    )
    assert relation == "unknown_scope"


def test_background_span_is_none():
    relation = decide_relation(
        claim_family_match=True,
        scope_a=_scope(),
        scope_b=_scope(),
        direction_a="associated",
        direction_b="associated",
        span_licenses=False,
    )
    assert relation == "none"


def test_i003_gold_pair_is_qualifies():
    item = load_document(ITEMS / "I003.yaml")
    relation = relation_from_claims(item["gold_claim"], item["compare_claim"])
    assert relation == "Qualifies"
    assert item["gold_claim"]["relation"] == "Qualifies"


def test_i003_same_scope_would_contradict():
    item = load_document(ITEMS / "I003.yaml")
    comparable = deepcopy(item["compare_claim"])
    comparable["scope"] = deepcopy(item["gold_claim"]["scope"])
    assert relation_from_claims(item["gold_claim"], comparable) == "Contradicts"


def test_five_items_present():
    items = load_all_gold_items()
    assert [i["item_id"] for i in items] == ["I001", "I002", "I003", "I004", "I005"]
