"""B4: SciFact-style polarity. Supports / Contradicts / none. No scope.

Wadden et al. 2020/2022 score SUPPORT / REFUTE / NEI from claim vs evidence
text. AskChem scores supports / contradicts without obligatory imaging scope.
This module is that public residual, not Paper 4. E1 Qualifies is not a
polarity label. Do not treat this output as gold.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = PACKAGE_ROOT / "corpus" / "pilot" / "sources"

# SciFact SUPPORT / REFUTE / NEI, mapped onto this folder's relation names
# that polarity is allowed to emit. Qualifies is out of scope for B4.
POLARITY_LABELS = ("Supports", "Contradicts", "none")

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

# Check negation first so "not associated" is not counted as associated.
NEGATION = re.compile(
    r"\b(?:is|was|are|were)?\s*not\s+associated\b|"
    r"\bno association\b|"
    r"\bnot related\b|"
    r"\bunrelated\b",
    re.IGNORECASE,
)
POSITIVE = re.compile(r"\bassociated\b|\bincreased\b|\bhigher\b", re.IGNORECASE)

TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
OVERLAP_THRESHOLD = 0.25


def tokenize(text: str) -> set[str]:
    return {
        tok
        for tok in TOKEN.findall(text.lower())
        if tok not in STOPWORDS and len(tok) > 2
    }


def overlap_coverage(claim_text: str, evidence_text: str) -> float:
    claim_toks = tokenize(claim_text)
    if not claim_toks:
        return 0.0
    return len(claim_toks & tokenize(evidence_text)) / len(claim_toks)


def keyword_polarity(text: str) -> str | None:
    """positive / negative from surface keywords. No scope fields."""
    if NEGATION.search(text or ""):
        return "negative"
    if POSITIVE.search(text or ""):
        return "positive"
    return None


def polarity_from_texts(
    claim_text: str,
    evidence_text: str,
    *,
    overlap_threshold: float = OVERLAP_THRESHOLD,
) -> str:
    """Claim vs evidence string only. Scope dicts are not arguments."""
    if overlap_coverage(claim_text, evidence_text) < overlap_threshold:
        return "none"
    claim_pol = keyword_polarity(claim_text)
    evid_pol = keyword_polarity(evidence_text)
    if claim_pol and evid_pol and claim_pol != evid_pol:
        return "Contradicts"
    if claim_pol or evid_pol or claim_pol == evid_pol:
        return "Supports"
    return "none"


def load_span_text(paper_id: str, paragraph_id: str) -> str:
    path = SOURCES_DIR / f"{paper_id}.yaml"
    if not path.is_file():
        return ""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for span in data.get("spans") or []:
        if span.get("paragraph_id") == paragraph_id:
            return str(span.get("text") or "").strip()
    return ""


def span_text_for_claim(claim: Mapping[str, Any]) -> str:
    span = claim.get("evidence_span") or {}
    if span.get("text"):
        return str(span["text"]).strip()
    paper_id = str(span.get("source") or claim.get("asserted_by") or "")
    paragraph_id = str(span.get("paragraph_id") or "")
    if paper_id and paragraph_id:
        return load_span_text(paper_id, paragraph_id)
    return ""


def polarity_from_item(item: Mapping[str, Any]) -> str:
    """Offline B4 label for a gold item. Ignores scope on purpose."""
    gold = item.get("gold_claim") or item
    compare = item.get("compare_claim")
    claim_text = str(gold.get("statement") or "")
    if compare is not None:
        return polarity_from_texts(claim_text, str(compare.get("statement") or ""))
    return polarity_from_texts(claim_text, span_text_for_claim(gold))
