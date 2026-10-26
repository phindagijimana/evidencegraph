"""E2/E3: coexisting epistemic states. Missing artifacts are not a failed reproduction."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

STATES = (
    "reported",
    "evidence_linked",
    "expert_adjudicated",
    "computationally_reproduced",
    "independently_replicated",
    "contested",
    "unknown_not_assessed",
)

MISSING_TOKENS = frozenset(
    {
        "",
        "unknown",
        "unavailable",
        "pending",
        "mentioned_readme_only",
        "n/a",
        "na",
        "none",
    }
)


def artifact_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, Mapping):
        if value.get("available") is False:
            return True
        ident = value.get("id") or value.get("digest") or value.get("path")
        return artifact_missing(ident)
    return str(value).strip().lower() in MISSING_TOKENS


def assign_reproducibility_states(
    existing: Iterable[str] | None,
    *,
    code_artifact: Any,
    workflow_run: Any,
) -> list[str]:
    """Keep coexisting labels. Missing code/run ⇒ unknown_not_assessed, never reproduced."""
    states = [s for s in (existing or []) if s in STATES]
    missing = artifact_missing(code_artifact) or artifact_missing(workflow_run)
    if missing:
        states = [s for s in states if s != "computationally_reproduced"]
        if "unknown_not_assessed" not in states:
            states.append("unknown_not_assessed")
    return states


def false_reproduction(
    claim: Mapping[str, Any],
    pred: Mapping[str, Any] | None = None,
) -> bool:
    """True when the system asserts computationally_reproduced without artifacts."""
    source = pred if pred is not None else claim
    states = list(source.get("epistemic_states") or [])
    if source.get("asserts_reproduced") is True:
        states.append("computationally_reproduced")
    artifacts = claim
    missing = artifact_missing(artifacts.get("code_artifact")) or artifact_missing(
        artifacts.get("workflow_run")
    )
    return missing and "computationally_reproduced" in states


def states_legal_for_missing_artifacts(
    states: Iterable[str],
    *,
    code_artifact: Any,
    workflow_run: Any,
) -> bool:
    missing = artifact_missing(code_artifact) or artifact_missing(workflow_run)
    labels = list(states)
    if not missing:
        return True
    if "computationally_reproduced" in labels:
        return False
    return "unknown_not_assessed" in labels
