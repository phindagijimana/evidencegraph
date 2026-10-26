"""Europe PMC client: URL builder, mocked OA/non-OA, network off, gated live."""

from __future__ import annotations

import json
import os
from urllib.parse import unquote

import pytest

from ingest.europepmc import (
    LIVE_ENV,
    NetworkDisabled,
    build_search_url,
    fetch_search,
    ingest_doi,
    live_ingest_enabled,
)
from ingest.resolve import LicenseRefused, ResolutionError

RESTRICTED_DOI = "10.9999/restricted-mock"
FIXTURE_DOI = "10.9999/eg.fixture.surgical-hs"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"


def _payload(result: dict) -> str:
    return json.dumps({"resultList": {"result": [result]}})


def test_build_search_url_is_europepmc_and_includes_doi():
    url = build_search_url(FIXTURE_DOI)
    assert url.startswith("https://www.ebi.ac.uk/europepmc/webservices/rest/search?")
    assert "format=json" in url
    assert "DOI" in url
    assert FIXTURE_DOI in unquote(url)
    assert "fullTextXML" not in url


def test_default_network_off_does_not_call_europepmc(monkeypatch):
    monkeypatch.delenv(LIVE_ENV, raising=False)
    assert live_ingest_enabled() is False
    with pytest.raises(NetworkDisabled, match="network is off"):
        fetch_search(FIXTURE_DOI)


def test_mocked_non_oa_is_refused_and_full_text_not_stored(tmp_path):
    leaked = tmp_path / "leak.txt"
    leaked.write_text(SECRET, encoding="utf-8")

    def opener(url: str) -> str:
        assert "europepmc" in url
        return _payload(
            {
                "doi": RESTRICTED_DOI,
                "isOpenAccess": "N",
                "license": "all-rights-reserved",
                "fullTextXml": SECRET,
                "title": "Mocked non-OA",
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


def test_mocked_oa_is_permitted_without_full_text(tmp_path):
    def opener(url: str) -> str:
        return _payload(
            {
                "doi": FIXTURE_DOI,
                "isOpenAccess": "Y",
                "license": "cc by",
                "title": "Fixture OA",
                "fullTextXml": "MUST NOT BE STORED",
                "pmcid": "PMC0",
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
    written = list(tmp_path.glob("*.epmc.meta.yaml"))
    assert written
    text = written[0].read_text(encoding="utf-8")
    assert "MUST NOT BE STORED" not in text
    assert "fullTextXml: null" in text or "full_text: null" in text


def test_empty_europepmc_payload_is_resolution_error():
    def opener(url: str) -> str:
        return json.dumps({"resultList": {"result": []}})

    with pytest.raises(ResolutionError, match="no Europe PMC result"):
        ingest_doi(FIXTURE_DOI, opener=opener)


@pytest.mark.skipif(
    os.environ.get(LIVE_ENV) != "1",
    reason="live Europe PMC call gated; set EG_LIVE_INGEST=1",
)
def test_live_europepmc_fixture_doi_does_not_store_full_text(tmp_path):
    with pytest.raises((ResolutionError, LicenseRefused)):
        ingest_doi(
            RESTRICTED_DOI,
            license_check=True,
            live=True,
            store_dir=tmp_path,
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert "<article" not in body
            assert "fullTextXml:" not in body or "fullTextXml: null" in body
