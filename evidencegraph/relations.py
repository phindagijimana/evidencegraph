"""E1: scope-conditioned relation decision.

Incomparable scope is Qualifies, not Contradicts. A citation is not support.
"""

from __future__ import annotations

from typing import Any, Mapping

RELATIONS = ("Supports", "Contradicts", "Qualifies", "unknown_scope", "none")

SCOPE_FIELDS = (
    "population",
    "acquisition",
    "method_identity",
    "comparator",
    "timepoint",
    "outcome_definition",
)

DECIDING_FIELDS = (
    "population",
    "acquisition",
    "method_identity",
    "comparator",
)

UNKNOWN_TOKENS = frozenset(
    {"", "unknown", "pending", "n/a", "na", "unavailable", "none"}
)


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip().lower() in UNKNOWN_TOKENS


def normalize(value: Any) -> str:
    return " ".join(str(value).strip().lower().split())


def scope_comparability(
    scope_a: Mapping[str, Any], scope_b: Mapping[str, Any]
) -> str:
    """Return comparable, incomparable, or insufficient."""
    known_pairs = 0
    diffs = 0
    for field in DECIDING_FIELDS:
        a = scope_a.get(field)
        b = scope_b.get(field)
        if is_unknown(a) or is_unknown(b):
            continue
        known_pairs += 1
        if normalize(a) != normalize(b):
            diffs += 1
    if known_pairs == 0:
        return "insufficient"
    if diffs:
        return "incomparable"
    return "comparable"


def same_direction(dir_a: Any, dir_b: Any) -> bool | None:
    if is_unknown(dir_a) or is_unknown(dir_b):
        return None
    return normalize(dir_a) == normalize(dir_b)


def span_licenses_claim(claim: Mapping[str, Any]) -> bool:
    span = claim.get("evidence_span") or {}
    if span.get("licenses_claim") is False:
        return False
    if span.get("licenses_claim") is True:
        return True
    role = str(span.get("role") or claim.get("span_role") or "").strip().lower()
    if role in {"background", "hypothesis", "related_work", "citation_only"}:
        return False
    if role == "finding":
        return True
    return False


def decide_relation(
    *,
    claim_family_match: bool,
    scope_a: Mapping[str, Any],
    scope_b: Mapping[str, Any],
    direction_a: Any = None,
    direction_b: Any = None,
    span_licenses: bool,
) -> str:
    if not span_licenses:
        return "none"
    if not claim_family_match:
        return "none"
    status = scope_comparability(scope_a, scope_b)
    if status == "insufficient":
        return "unknown_scope"
    if status == "incomparable":
        return "Qualifies"
    matched = same_direction(direction_a, direction_b)
    if matched is None:
        return "unknown_scope"
    return "Supports" if matched else "Contradicts"


def _family(claim: Mapping[str, Any]) -> str | None:
    raw = claim.get("claim_family") or claim.get("outcome_family")
    if is_unknown(raw):
        return None
    return normalize(raw)


def relation_from_claims(
    claim_a: Mapping[str, Any],
    claim_b: Mapping[str, Any] | None = None,
    *,
    span_licenses: bool | None = None,
) -> str:
    """Compare two claims, or a claim against its own span/scope."""
    other = claim_b if claim_b is not None else claim_a
    if span_licenses is None:
        if claim_b is None:
            span_licenses = span_licenses_claim(claim_a)
        else:
            span_licenses = span_licenses_claim(claim_a) and span_licenses_claim(
                other
            )
    fam_a, fam_b = _family(claim_a), _family(other)
    family_match = True if fam_a is None or fam_b is None else fam_a == fam_b
    return decide_relation(
        claim_family_match=family_match,
        scope_a=claim_a.get("scope") or {},
        scope_b=other.get("scope") or {},
        direction_a=claim_a.get("effect_direction"),
        direction_b=other.get("effect_direction"),
        span_licenses=span_licenses,
    )
