"""Public substrate: SciFact-style polarity (no scope) + license refuse.

Offline fixtures only. No Europe PMC / Crossref network call.
B4 is not the paper. Extraction is not gold.
"""

from __future__ import annotations

from copy import deepcopy

import pytest

from baselines.polarity import polarity_from_item, polarity_from_texts
from evaluation.score import load_all_gold_items
from graph.store import load_document
from ingest.resolve import LicenseRefused, ResolutionError, resolve
from tests.conftest import ITEMS

RESTRICTED_DOI = "10.9999/restricted-mock"
POLARITY_OK = {"Supports", "Contradicts", "none"}


def _item(item_id: str) -> dict:
    return load_document(ITEMS / f"{item_id}.yaml")


def test_mocked_restricted_doi_refused_offline():
    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            RESTRICTED_DOI,
            license_check=True,
            metadata={
                "doi": RESTRICTED_DOI,
                "license": "all-rights-reserved",
                "is_oa": False,
                "full_text": "RESTRICTED MOCK TEXT",
            },
        )


def test_manifest_restricted_doi_refused_without_network():
    with pytest.raises(LicenseRefused):
        resolve(RESTRICTED_DOI, license_check=True)


def test_unknown_doi_does_not_call_europepmc():
    with pytest.raises(ResolutionError, match="network is off"):
        resolve("10.1234/not-in-manifest", license_check=True)


def test_i003_polarity_may_contradict_or_support():
    """SciFact already owns polarity without imaging scope (B4 residual)."""
    label = polarity_from_item(_item("I003"))
    assert label in {"Contradicts", "Supports"}
    assert label in POLARITY_OK
    assert label != "Qualifies"


def test_i002_background_span_polarity_none():
    label = polarity_from_item(_item("I002"))
    assert label == "none"


def test_i001_finding_span_polarity_supports():
    label = polarity_from_item(_item("I001"))
    assert label == "Supports"


def test_polarity_ignores_scope_fields():
    item = deepcopy(_item("I003"))
    before = polarity_from_item(item)
    item["gold_claim"]["scope"] = {
        "population": "community epilepsy cohort",
        "acquisition": "1.5T community MRI",
        "method_identity": "ASHS",
        "comparator": "imaging-defined hippocampal sclerosis",
        "timepoint": "outpatient",
        "outcome_definition": "hippocampal asymmetry associated with HS",
    }
    item["compare_claim"]["scope"] = dict(item["gold_claim"]["scope"])
    after = polarity_from_item(item)
    assert before == after
    assert after in {"Contradicts", "Supports"}


def test_polarity_from_texts_has_no_scope_argument():
    label = polarity_from_texts(
        "Hippocampal asymmetry is associated with hippocampal sclerosis.",
        "Hippocampal asymmetry is not associated with hippocampal sclerosis.",
    )
    assert label == "Contradicts"


def test_five_gold_items_polarity_offline():
    items = load_all_gold_items()
    assert [i["item_id"] for i in items] == ["I001", "I002", "I003", "I004", "I005"]
    for item in items:
        assert polarity_from_item(item) in POLARITY_OK
