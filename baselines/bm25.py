"""B0: BM25 over permitted fixture spans only. Offline. Not a RAG product.

Robertson / Spark Jones BM25 on hand-authored spans under corpus/pilot/sources/.
Restricted rows (no spans_path, non-OA) are excluded. This is the B0/B2-shaped
retrieval residual in methods §2, not EvidenceGraph scoring (B6).
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from ingest.resolve import DEFAULT_MANIFEST, is_redistributable_oa, load_manifest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = PACKAGE_ROOT / "corpus" / "pilot" / "sources"

TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "was",
        "are",
        "were",
        "be",
        "with",
        "in",
        "of",
        "and",
        "to",
        "for",
        "this",
        "that",
        "or",
        "on",
        "by",
        "as",
        "from",
        "into",
        "its",
        "it",
        "not",
    }
)

K1 = 1.2
B = 0.75


def tokenize(text: str) -> list[str]:
    return [
        tok
        for tok in TOKEN.findall((text or "").lower())
        if tok not in STOPWORDS and len(tok) > 2
    ]


def _span_id(paper_id: str, paragraph_id: str) -> str:
    return f"{paper_id}#{paragraph_id}"


def load_permitted_spans(
    *,
    manifest_path: Path | None = None,
    sources_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Load OA fixture spans only. Never includes restricted / no-span rows."""
    manifest = load_manifest(manifest_path or DEFAULT_MANIFEST)
    root = sources_dir or SOURCES_DIR
    docs: list[dict[str, Any]] = []
    for paper in manifest.get("papers") or []:
        if not paper.get("fixture"):
            continue
        if paper.get("spans_path") in (None, ""):
            continue
        if not is_redistributable_oa(paper):
            continue
        paper_id = str(paper.get("paper_id") or "")
        path = root / f"{paper_id}.yaml"
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for span in data.get("spans") or []:
            text = str(span.get("text") or "").strip()
            if not text:
                continue
            paragraph_id = str(span.get("paragraph_id") or "")
            docs.append(
                {
                    "doc_id": _span_id(paper_id, paragraph_id),
                    "paper_id": paper_id,
                    "paragraph_id": paragraph_id,
                    "role": span.get("role"),
                    "licenses_claim": bool(span.get("licenses_claim")),
                    "text": text,
                    "tokens": tokenize(text),
                    "fixture": True,
                    "doi": paper.get("doi"),
                    "not_a_published_doi": bool(paper.get("not_a_published_doi", True)),
                }
            )
    return docs


def _idf(n_qi: int, n_docs: int) -> float:
    # Lucene-style IDF: stays non-negative on small fixture corpora.
    return math.log(1.0 + (n_docs - n_qi + 0.5) / (n_qi + 0.5))


def _average_length(docs: Sequence[Mapping[str, Any]]) -> float:
    if not docs:
        return 0.0
    total = sum(len(doc.get("tokens") or []) for doc in docs)
    return total / len(docs)


def bm25_score(
    query_tokens: Sequence[str],
    doc_tokens: Sequence[str],
    *,
    df: Mapping[str, int],
    n_docs: int,
    avgdl: float,
    k1: float = K1,
    b: float = B,
) -> float:
    if not query_tokens or not doc_tokens or n_docs <= 0:
        return 0.0
    tf: dict[str, int] = {}
    for tok in doc_tokens:
        tf[tok] = tf.get(tok, 0) + 1
    dl = len(doc_tokens)
    denom_norm = k1 * (1.0 - b + b * (dl / avgdl)) if avgdl else k1
    score = 0.0
    seen: set[str] = set()
    for tok in query_tokens:
        if tok in seen:
            continue
        seen.add(tok)
        freq = tf.get(tok, 0)
        if freq == 0:
            continue
        idf = _idf(df.get(tok, 0), n_docs)
        score += idf * (freq * (k1 + 1.0)) / (freq + denom_norm)
    return score


def _document_frequency(docs: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    df: dict[str, int] = {}
    for doc in docs:
        for tok in set(doc.get("tokens") or []):
            df[tok] = df.get(tok, 0) + 1
    return df


def rank_spans(
    query: str,
    *,
    docs: Sequence[Mapping[str, Any]] | None = None,
    k: int = 10,
) -> list[dict[str, Any]]:
    """Rank permitted fixture spans. Offline. B0 only — not gold attribution."""
    corpus = list(docs) if docs is not None else load_permitted_spans()
    query_tokens = tokenize(query)
    if not query_tokens or not corpus:
        return []
    df = _document_frequency(corpus)
    avgdl = _average_length(corpus)
    n_docs = len(corpus)
    ranked: list[dict[str, Any]] = []
    for doc in corpus:
        score = bm25_score(
            query_tokens,
            list(doc.get("tokens") or []),
            df=df,
            n_docs=n_docs,
            avgdl=avgdl,
        )
        ranked.append(
            {
                "doc_id": doc.get("doc_id"),
                "paper_id": doc.get("paper_id"),
                "paragraph_id": doc.get("paragraph_id"),
                "role": doc.get("role"),
                "licenses_claim": doc.get("licenses_claim"),
                "score": score,
                "text": doc.get("text"),
                "arm": "B0",
            }
        )
    ranked.sort(key=lambda hit: (-float(hit["score"]), str(hit["doc_id"])))
    return ranked[: max(0, k)]


def retrieve(query: str, *, k: int = 10) -> list[dict[str, Any]]:
    return rank_spans(query, k=k)


def iter_span_ids(docs: Iterable[Mapping[str, Any]] | None = None) -> list[str]:
    corpus = list(docs) if docs is not None else load_permitted_spans()
    return [str(doc["doc_id"]) for doc in corpus]
