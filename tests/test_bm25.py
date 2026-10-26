"""B0 BM25 over permitted fixture spans. Offline. Not gold attribution."""

from __future__ import annotations

from baselines.bm25 import load_permitted_spans, rank_spans, tokenize


def _i001_span_query() -> str:
    """Query the I001 finding span, not a claim paraphrase."""
    for doc in load_permitted_spans():
        if doc["doc_id"] == "P-HS-SURGICAL-001#results-p2":
            return str(doc["text"])
    raise AssertionError("I001 finding span missing from fixture corpus")


def test_permitted_spans_exclude_restricted_and_are_fixtures():
    docs = load_permitted_spans()
    ids = {doc["paper_id"] for doc in docs}
    assert "P-RESTRICTED-MOCK" not in ids
    assert "P-HS-SURGICAL-001" in ids
    assert "P-HS-ATLAS-004" in ids
    assert "P-HS-FIELDSTRENGTH-005" in ids
    assert "P-HS-CONNECTOME-006" in ids
    for doc in docs:
        assert doc["fixture"] is True
        assert doc["tokens"]
        assert doc["not_a_published_doi"] is True
        assert str(doc.get("doi") or "").startswith("10.9999/eg.fixture.")


def test_i001_finding_ranks_above_background():
    query = _i001_span_query()
    assert "FreeSurfer" in query
    hits = rank_spans(query, k=20)
    assert hits
    by_id = {hit["doc_id"]: hit for hit in hits}
    finding = by_id["P-HS-SURGICAL-001#results-p2"]
    background = by_id["P-HS-SURGICAL-001#background-p1"]
    assert finding["score"] > background["score"]
    assert finding["role"] == "finding"
    assert background["role"] == "background"
    assert hits[0]["paper_id"] == "P-HS-SURGICAL-001"
    assert hits[0]["paragraph_id"] == "results-p2"


def test_bm25_two_span_unit():
    docs = [
        {
            "doc_id": "P-HS-SURGICAL-001#results-p2",
            "paper_id": "P-HS-SURGICAL-001",
            "paragraph_id": "results-p2",
            "role": "finding",
            "licenses_claim": True,
            "text": "surgical epilepsy FreeSurfer pathology-defined hippocampal sclerosis",
            "tokens": tokenize(
                "surgical epilepsy FreeSurfer pathology-defined hippocampal sclerosis"
            ),
        },
        {
            "doc_id": "P-HS-SURGICAL-001#background-p1",
            "paper_id": "P-HS-SURGICAL-001",
            "paragraph_id": "background-p1",
            "role": "background",
            "licenses_claim": False,
            "text": "hippocampus memory preoperative MRI",
            "tokens": tokenize("hippocampus memory preoperative MRI"),
        },
    ]
    hits = rank_spans(
        "FreeSurfer pathology-defined hippocampal sclerosis surgical",
        docs=docs,
        k=2,
    )
    assert hits[0]["paragraph_id"] == "results-p2"
    assert hits[0]["score"] > hits[1]["score"]


def test_empty_query_returns_no_hits():
    assert rank_spans("   ", k=5) == []
