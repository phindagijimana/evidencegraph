"""E4: scoped attribution score. No LLM judge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from evidencegraph.relations import SCOPE_FIELDS, normalize, relation_from_claims
from evidencegraph.states import false_reproduction
from graph.store import PACKAGE_ROOT, load_document

SCORE_SCHEMA_PATH = PACKAGE_ROOT / "schema" / "score.schema.json"


def _norm_text(value: Any) -> str:
    return normalize(value) if value is not None else ""


def _claim_from_pred(pred: Mapping[str, Any]) -> dict[str, Any]:
    if "gold_claim" in pred:
        return dict(pred["gold_claim"])
    if "claim" in pred and isinstance(pred["claim"], Mapping):
        return dict(pred["claim"])
    return dict(pred)


def scopes_match(gold: Mapping[str, Any], pred: Mapping[str, Any]) -> bool:
    g_scope = gold.get("scope") or {}
    p_scope = pred.get("scope") or {}
    for field in SCOPE_FIELDS:
        if _norm_text(g_scope.get(field)) != _norm_text(p_scope.get(field)):
            return False
    return True


def spans_match(gold: Mapping[str, Any], pred: Mapping[str, Any]) -> bool:
    g = gold.get("evidence_span") or {}
    p = pred.get("evidence_span") or {}
    if _norm_text(g.get("source")) != _norm_text(p.get("source")):
        return False
    if g.get("paragraph_id") and p.get("paragraph_id"):
        if g["paragraph_id"] != p["paragraph_id"]:
            return False
    g_off, p_off = g.get("offsets"), p.get("offsets")
    if g_off not in (None, "pending") and p_off not in (None, "pending"):
        return list(g_off) == list(p_off)
    if g.get("paragraph_id") or p.get("paragraph_id"):
        return g.get("paragraph_id") == p.get("paragraph_id")
    return False


def claims_match(gold: Mapping[str, Any], pred: Mapping[str, Any]) -> bool:
    if gold.get("claim_id") and pred.get("claim_id"):
        if gold["claim_id"] != pred["claim_id"]:
            return False
    return _norm_text(gold.get("statement")) == _norm_text(pred.get("statement"))


def sources_match(gold: Mapping[str, Any], pred: Mapping[str, Any]) -> bool:
    g_src = (gold.get("evidence_span") or {}).get("source") or gold.get("asserted_by")
    p_src = (pred.get("evidence_span") or {}).get("source") or pred.get("asserted_by")
    return _norm_text(g_src) == _norm_text(p_src)


def attribution_tuple_match(gold: Mapping[str, Any], pred: Mapping[str, Any]) -> dict[str, bool]:
    claim_ok = claims_match(gold, pred)
    source_ok = sources_match(gold, pred)
    span_ok = spans_match(gold, pred)
    scope_ok = scopes_match(gold, pred)
    return {
        "claim": claim_ok,
        "source": source_ok,
        "span": span_ok,
        "scope": scope_ok,
        "all": claim_ok and source_ok and span_ok and scope_ok,
    }


def _pred_relation(item: Mapping[str, Any], pred: Mapping[str, Any], pred_claim: Mapping[str, Any]) -> str:
    if pred.get("relation") in {None, ""} and "relation" not in pred_claim:
        gold = item.get("gold_claim") or {}
        compare = item.get("compare_claim")
        pred_compare = pred.get("compare_claim")
        if compare is not None and pred_compare is not None:
            return relation_from_claims(pred_claim, pred_compare)
        return relation_from_claims(pred_claim)
    return str(pred.get("relation") or pred_claim.get("relation"))


def score_item(
    item: Mapping[str, Any],
    pred: Mapping[str, Any],
    *,
    arm: str = "B6",
) -> dict[str, Any]:
    gold = dict(item.get("gold_claim") or item)
    pred_claim = _claim_from_pred(pred)
    gold_compare = item.get("compare_claim")
    pred_compare = pred.get("compare_claim")

    parts = attribution_tuple_match(gold, pred_claim)
    span_ok = parts["span"]
    scope_ok = parts["scope"]
    attribution_ok = parts["all"]
    if gold_compare is not None:
        if pred_compare is None:
            attribution_ok = False
            span_ok = False
            scope_ok = False
        else:
            other = attribution_tuple_match(gold_compare, pred_compare)
            attribution_ok = attribution_ok and other["all"]
            span_ok = span_ok and other["span"]
            scope_ok = scope_ok and other["scope"]

    relation_gold = str(item.get("relation_gold") or gold.get("relation"))
    if gold_compare is not None:
        relation_gold = str(gold.get("relation") or "Qualifies")
    relation_pred = _pred_relation(item, pred, pred_claim)

    gold_states = list(gold.get("epistemic_states") or [])
    pred_states = list(
        pred.get("epistemic_states") or pred_claim.get("epistemic_states") or []
    )
    pred_for_repro = {
        "epistemic_states": pred_states,
        "asserts_reproduced": pred.get("asserts_reproduced"),
        "code_artifact": pred_claim.get("code_artifact", gold.get("code_artifact")),
        "workflow_run": pred_claim.get("workflow_run", gold.get("workflow_run")),
    }
    false_repro = false_reproduction(gold, pred_for_repro)

    unsupported = bool(item.get("unsupported")) or relation_gold == "none"
    if pred.get("unsupported") is True or relation_pred == "none":
        unsupported = True
    if relation_pred == "Supports" and relation_gold == "none":
        unsupported = True

    abstained = bool(pred.get("abstained") or pred.get("abstain"))
    if relation_pred == "unknown_scope":
        abstained = True

    score = {
        "item_id": item.get("item_id") or gold.get("claim_id"),
        "paper_ids": list(item.get("paper_ids") or [gold.get("asserted_by")]),
        "family": item.get("family") or "attribution",
        "arm": arm,
        "attribution_correct": bool(attribution_ok),
        "unsupported": bool(unsupported),
        "abstained": bool(abstained),
        "span_correct": bool(span_ok),
        "scope_correct": bool(scope_ok),
        "relation_gold": relation_gold,
        "relation_predicted": relation_pred,
        "epistemic_states_gold": gold_states,
        "epistemic_states_predicted": pred_states,
        "false_reproduction": bool(false_repro),
        "construction": item.get("construction")
        or gold.get("construction")
        or {"origin": "expert_entered", "extraction_is_gold": False},
        "infrastructure_failure": False,
    }
    validate_score(score)
    return score


def validate_score(score: Mapping[str, Any]) -> None:
    schema = json.loads(SCORE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(dict(score), schema)


def dump_score(score: Mapping[str, Any], path: Path) -> None:
    Path(path).write_text(json.dumps(score, indent=2) + "\n", encoding="utf-8")


def load_item(path: Path) -> dict[str, Any]:
    return load_document(path)


def gold_items_dir() -> Path:
    return PACKAGE_ROOT / "evaluation" / "items"


def load_all_gold_items() -> list[dict[str, Any]]:
    items = []
    for path in sorted(gold_items_dir().glob("I00*.yaml")):
        items.append(load_document(path))
    return items


def item_as_pred(item: Mapping[str, Any]) -> dict[str, Any]:
    """Identity prediction from gold (expert-entered; not extraction)."""
    pred = {
        "claim": dict(item["gold_claim"]),
        "relation": item["gold_claim"].get("relation"),
        "epistemic_states": list(item["gold_claim"].get("epistemic_states") or []),
        "construction": {"origin": "expert_entered", "extraction_is_gold": False},
    }
    if item.get("compare_claim"):
        pred["compare_claim"] = dict(item["compare_claim"])
    return pred
