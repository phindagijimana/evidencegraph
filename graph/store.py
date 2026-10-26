"""YAML claim store. Distinguishes expert-entered from machine-extracted."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from evidencegraph.relations import RELATIONS, SCOPE_FIELDS
from evidencegraph.states import STATES, assign_reproducibility_states

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CLAIM_FIELDS = (
    "claim_id",
    "asserted_by",
    "statement",
    "scope",
    "evidence_span",
    "relation",
    "epistemic_states",
    "workflow_run",
)


def load_document(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping in {path}")
    return data


def iter_claims(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    if "gold_claim" in document:
        claims = [dict(document["gold_claim"])]
        if document.get("compare_claim"):
            claims.append(dict(document["compare_claim"]))
        return claims
    if "claim_id" in document:
        return [dict(document)]
    raise ValueError("document is neither a claim nor a gold item")


def validate_claim(claim: Mapping[str, Any]) -> None:
    missing = [f for f in REQUIRED_CLAIM_FIELDS if f not in claim]
    if missing:
        raise ValueError(f"claim missing required fields: {missing}")
    scope = claim.get("scope") or {}
    absent_scope = [f for f in SCOPE_FIELDS if f not in scope]
    if absent_scope:
        raise ValueError(f"scope missing fields: {absent_scope}")
    span = claim.get("evidence_span") or {}
    if "source" not in span:
        raise ValueError("evidence_span.source is required")
    if not span.get("offsets") and not span.get("paragraph_id"):
        raise ValueError("evidence_span needs offsets or paragraph_id")
    if claim.get("relation") not in RELATIONS:
        raise ValueError(f"unknown relation: {claim.get('relation')}")
    for state in claim.get("epistemic_states") or []:
        if state not in STATES:
            raise ValueError(f"unknown epistemic state: {state}")


def normalize_claim(claim: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(claim)
    construction = dict(record.get("construction") or {})
    construction.setdefault("origin", "expert_entered")
    construction.setdefault("extraction_is_gold", False)
    record["construction"] = construction
    record["epistemic_states"] = assign_reproducibility_states(
        record.get("epistemic_states"),
        code_artifact=record.get("code_artifact"),
        workflow_run=record.get("workflow_run"),
    )
    if record["construction"]["origin"] == "machine_extracted":
        record["construction"]["extraction_is_gold"] = False
    validate_claim(record)
    return record


def to_jsonld(claim: Mapping[str, Any]) -> dict[str, Any]:
    construction = claim.get("construction") or {}
    return {
        "@context": {
            "eg": "https://evidencegraph.local/",
            "prov": "http://www.w3.org/ns/prov#",
        },
        "@type": "eg:Claim",
        "eg:claim_id": claim.get("claim_id"),
        "eg:statement": claim.get("statement"),
        "eg:relation": claim.get("relation"),
        "eg:scope": claim.get("scope"),
        "eg:epistemic_states": list(claim.get("epistemic_states") or []),
        "eg:origin": construction.get("origin", "expert_entered"),
        "eg:extraction_is_gold": bool(construction.get("extraction_is_gold", False)),
        "eg:workflow_run": claim.get("workflow_run"),
        "prov:wasDerivedFrom": (claim.get("evidence_span") or {}).get("source"),
    }


class ClaimStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, claim: Mapping[str, Any]) -> dict[str, Any]:
        record = normalize_claim(claim)
        dest = self.root / f"{record['claim_id']}.yaml"
        dest.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
        jsonld_path = self.root / f"{record['claim_id']}.jsonld.yaml"
        jsonld_path.write_text(
            yaml.safe_dump(to_jsonld(record), sort_keys=False), encoding="utf-8"
        )
        return record

    def load_path(self, path: Path) -> list[dict[str, Any]]:
        document = load_document(path)
        return [self.put(claim) for claim in iter_claims(document)]

    def get(self, claim_id: str) -> dict[str, Any] | None:
        dest = self.root / f"{claim_id}.yaml"
        if not dest.exists():
            return None
        return load_document(dest)

    def jsonld(self, claim_id: str) -> dict[str, Any] | None:
        dest = self.root / f"{claim_id}.jsonld.yaml"
        if not dest.exists():
            record = self.get(claim_id)
            return to_jsonld(record) if record else None
        return load_document(dest)

    def all_claims(self) -> Iterable[dict[str, Any]]:
        for path in sorted(self.root.glob("*.yaml")):
            if path.name.endswith(".jsonld.yaml"):
                continue
            yield load_document(path)
