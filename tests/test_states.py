"""E2/E3: missing code is unknown_not_assessed, not computationally_reproduced."""

from __future__ import annotations

from graph.store import ClaimStore, load_document
from evidencegraph.states import (
    assign_reproducibility_states,
    false_reproduction,
    states_legal_for_missing_artifacts,
)
from tests.conftest import ITEMS


def test_missing_code_is_unknown_not_assessed():
    states = assign_reproducibility_states(
        ["reported"],
        code_artifact="unavailable",
        workflow_run="unavailable",
    )
    assert "unknown_not_assessed" in states
    assert "computationally_reproduced" not in states


def test_mentioned_readme_is_not_reproduced():
    states = assign_reproducibility_states(
        ["reported", "computationally_reproduced"],
        code_artifact="mentioned_readme_only",
        workflow_run="unavailable",
    )
    assert "unknown_not_assessed" in states
    assert "computationally_reproduced" not in states


def test_i004_gold_is_unknown_not_reproduced():
    item = load_document(ITEMS / "I004.yaml")
    claim = item["gold_claim"]
    assert "unknown_not_assessed" in claim["epistemic_states"]
    assert "computationally_reproduced" not in claim["epistemic_states"]
    assert states_legal_for_missing_artifacts(
        claim["epistemic_states"],
        code_artifact=claim["code_artifact"],
        workflow_run=claim["workflow_run"],
    )


def test_asserting_reproduced_without_artifacts_is_false_reproduction():
    gold = {
        "code_artifact": "unavailable",
        "workflow_run": "unavailable",
        "epistemic_states": ["reported", "unknown_not_assessed"],
    }
    pred = {"epistemic_states": ["reported", "computationally_reproduced"]}
    assert false_reproduction(gold, pred) is True


def test_states_coexist_on_store_load(tmp_path):
    item = load_document(ITEMS / "I001.yaml")
    store = ClaimStore(tmp_path)
    stored = store.put(item["gold_claim"])
    assert "reported" in stored["epistemic_states"]
    assert "unknown_not_assessed" in stored["epistemic_states"]
    assert stored["construction"]["extraction_is_gold"] is False
