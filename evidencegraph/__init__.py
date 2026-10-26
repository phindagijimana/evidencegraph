"""EvidenceGraph: binding and scoring protocol for published claims (Paper 4)."""

from evidencegraph.relations import decide_relation, relation_from_claims
from evidencegraph.states import assign_reproducibility_states, false_reproduction

__all__ = [
    "decide_relation",
    "relation_from_claims",
    "assign_reproducibility_states",
    "false_reproduction",
]
