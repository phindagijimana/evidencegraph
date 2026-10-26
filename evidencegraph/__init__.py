"""EvidenceGraph public API. Scoped claim–evidence. Extraction is not gold."""

from evidencegraph.api import ingest, load
from evidencegraph.relations import decide_relation, relation_from_claims
from evidencegraph.states import assign_reproducibility_states, false_reproduction

__all__ = [
    "load",
    "ingest",
    "decide_relation",
    "relation_from_claims",
    "assign_reproducibility_states",
    "false_reproduction",
]
__version__ = "0.1.0"
