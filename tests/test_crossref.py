"""Crossref client: URL builder, mocked OA/non-OA, network off, gated live."""

from __future__ import annotations

import json
import os
from urllib.parse import unquote

import pytest

from ingest.crossref import (
    LIVE_ENV,
    NetworkDisabled,
    build_works_url,
    fetch_works,
    ingest_doi,
    live_ingest_enabled,
    map_license_url,
)
from ingest.resolve import LicenseRefused, ResolutionError

RESTRICTED_DOI = "10.9999/restricted-mock"
FIXTURE_DOI = "10.9999/eg.fixture.surgical-hs"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"
ABSTRACT = "MUST NOT BE STORED CROSSREF ABSTRACT"


def _works(message: dict) -> str:
    return json.dumps({"status": "ok", "message-type": "work", "message": message})


def test_build_works_url_is_crossref_and_includes_doi():
    url = build_works_url(FIXTURE_DOI)
    assert url.startswith("https://api.crossref.org/works/")
    assert FIXTURE_DOI in unquote(url)
    assert "fullText" not in url


def test_map_cc_by_license_url():
    assert map_license_url("https://creativecommons.org/licenses/by/4.0") == "cc-by-4.0"
    assert map_license_url("https://www.elsevier.com/tdm/userlicense/1.0/") == ""


def test_default_network_off_does_not_call_crossref(monkeypatch):
    monkeypatch.delenv(LIVE_ENV, raising=False)
    assert live_ingest_enabled() is False
    with pytest.raises(NetworkDisabled, match="network is off"):
        fetch_works(FIXTURE_DOI)


def test_mocked_non_oa_is_refused_and_full_text_not_stored(tmp_path):
    leaked = tmp_path / "leak.txt"
    leaked.write_text(SECRET, encoding="utf-8")

    def opener(url: str) -> str:
        assert "api.crossref.org/works" in url
        return _works(
            {
                "DOI": RESTRICTED_DOI,
                "title": ["Mocked non-OA"],
                "license": [{"URL": "https://www.elsevier.com/tdm/userlicense/1.0/"}],
                "abstract": SECRET,
            }
        )

    with pytest.raises(LicenseRefused, match="not redistributable"):
        ingest_doi(
            RESTRICTED_DOI,
            license_check=True,
            opener=opener,
            store_dir=tmp_path,
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert SECRET not in path.read_text(encoding="utf-8", errors="ignore")


def test_mocked_oa_is_permitted_without_abstract_or_full_text(tmp_path):
    def opener(url: str) -> str:
        return _works(
            {
                "DOI": FIXTURE_DOI,
                "title": ["Fixture OA"],
                "license": [{"URL": "https://creativecommons.org/licenses/by/4.0"}],
                "publisher": "Fixture Press",
                "abstract": ABSTRACT,
                "link": [
                    {
                        "URL": "https://example.org/must-not-fetch.pdf",
                        "content-type": "application/pdf",
                    }
                ],
            }
        )

    record = ingest_doi(
        FIXTURE_DOI,
        license_check=True,
        opener=opener,
        store_dir=tmp_path,
    )
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["full_text_stored"] is False
    assert record["abstract"] is None
    assert record["license"] == "cc-by-4.0"
    written = list(tmp_path.glob("*.crossref.meta.yaml"))
    assert written
    text = written[0].read_text(encoding="utf-8")
    assert ABSTRACT not in text
    assert "must-not-fetch.pdf" not in text
    assert SECRET not in text


def test_empty_crossref_payload_is_resolution_error():
    def opener(url: str) -> str:
        return json.dumps({"status": "ok", "message": None})

    with pytest.raises(ResolutionError, match="no Crossref works message"):
        ingest_doi(FIXTURE_DOI, opener=opener)


@pytest.mark.skipif(
    os.environ.get(LIVE_ENV) != "1",
    reason="live Crossref call gated; set EG_LIVE_INGEST=1",
)
def test_live_crossref_does_not_store_full_text(tmp_path):
    record = ingest_doi(
        "10.1038/sdata.2016.44",
        license_check=True,
        live=True,
        store_dir=tmp_path,
    )
    assert record["full_text"] is None
    assert record["abstract"] is None
    assert record["full_text_stored"] is False
    for path in tmp_path.rglob("*"):
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert "<article" not in body
            assert "defined modern neuroimaging" not in body
