"""Read-path queries. No model API."""

from __future__ import annotations

from typing import Any

from graph.store import ClaimStore, to_jsonld


def query_claim(
    store: ClaimStore, claim_id: str, *, show_scope: bool = False
) -> dict[str, Any] | None:
    record = store.get(claim_id)
    if record is None:
        return None
    payload: dict[str, Any] = {
        "claim_id": record.get("claim_id"),
        "statement": record.get("statement"),
        "relation": record.get("relation"),
        "epistemic_states": list(record.get("epistemic_states") or []),
        "workflow_run": record.get("workflow_run"),
        "construction": record.get("construction"),
        "jsonld": to_jsonld(record),
    }
    if show_scope:
        payload["scope"] = record.get("scope")
        payload["evidence_span"] = record.get("evidence_span")
    return payload
