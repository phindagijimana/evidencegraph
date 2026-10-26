"""Public baselines for Paper 4. Not the EvidenceGraph methods.

B0 is BM25 over permitted fixture spans (baselines/bm25.py).
B4 is SciFact-style polarity (Wadden et al. 2020/2022) without imaging scope.
License refuse reuses Europe PMC / Crossref field names in ingest/resolve.py.
"""

from baselines.bm25 import load_permitted_spans, rank_spans, retrieve
from baselines.polarity import polarity_from_item, polarity_from_texts

__all__ = [
    "load_permitted_spans",
    "polarity_from_item",
    "polarity_from_texts",
    "rank_spans",
    "retrieve",
]
