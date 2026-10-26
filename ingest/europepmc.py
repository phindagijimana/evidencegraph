"""Europe PMC ingest client. Builds the request URL. Default network off.

Reuses Europe PMC search field names (isOpenAccess, license). Does not replace
ingest/resolve.py. A live HTTP call runs only when EG_LIVE_INGEST=1.
Never stores restricted full text.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

from ingest.resolve import (
    FULL_TEXT_KEYS,
    LicenseRefused,
    ResolutionError,
    is_redistributable_oa,
    strip_restricted_payload,
)

EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
LIVE_ENV = "EG_LIVE_INGEST"

Opener = Callable[[str], str]


class NetworkDisabled(Exception):
    """Network is off. Europe PMC is not called unless EG_LIVE_INGEST=1."""


def live_ingest_enabled() -> bool:
    return os.environ.get(LIVE_ENV, "") == "1"


def build_search_url(doi: str, *, result_type: str = "core", page_size: int = 1) -> str:
    """Construct the Europe PMC REST search URL. Does not perform I/O."""
    key = (doi or "").strip()
    if not key:
        raise ResolutionError("DOI is required to build a Europe PMC URL")
    query = f'DOI:"{key}"'
    params = urlencode(
        {
            "query": query,
            "resultType": result_type,
            "format": "json",
            "pageSize": str(page_size),
        }
    )
    return f"{EUROPEPMC_SEARCH}?{params}"


def is_open_access(result: Mapping[str, Any] | None) -> bool:
    if not result:
        return False
    flag = str(result.get("isOpenAccess") or "").strip().upper()
    if flag == "N" or result.get("is_oa") is False:
        return False
    if flag != "Y" and result.get("is_oa") is not True:
        return False
    mapped = {
        "doi": result.get("doi"),
        "license": result.get("license"),
        "is_oa": True,
        "europepmc": {
            "isOpenAccess": result.get("isOpenAccess") or "Y",
            "license": result.get("license"),
        },
    }
    return is_redistributable_oa(mapped)


def strip_full_text(record: Mapping[str, Any]) -> dict[str, Any]:
    return strip_restricted_payload(record)


def first_result(payload: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None
    hit_list = (payload.get("resultList") or {}).get("result") or []
    if not hit_list:
        return None
    first = hit_list[0]
    return dict(first) if isinstance(first, Mapping) else None


def parse_search_payload(raw: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    return json.loads(raw)


def _http_get(url: str, *, timeout: float = 20.0) -> str:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "evidencegraph/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_search(
    doi: str,
    *,
    opener: Opener | None = None,
    live: bool | None = None,
) -> dict[str, Any]:
    """Return a parsed Europe PMC search payload. Network off unless gated or mocked."""
    url = build_search_url(doi)
    allowed = live_ingest_enabled() if live is None else bool(live)
    if opener is not None:
        raw = opener(url)
        return parse_search_payload(raw)
    if not allowed:
        raise NetworkDisabled(
            f"network is off; Europe PMC not called for {doi}. "
            f"Set {LIVE_ENV}=1 for a live call"
        )
    return parse_search_payload(_http_get(url))


def metadata_from_result(result: Mapping[str, Any], *, doi: str) -> dict[str, Any]:
    record = strip_full_text(result)
    license_name = record.get("license")
    oa_flag = str(record.get("isOpenAccess") or "").upper() == "Y"
    return {
        "doi": record.get("doi") or doi,
        "pmcid": record.get("pmcid"),
        "title": record.get("title"),
        "license": license_name,
        "is_oa": oa_flag,
        "redistributable": oa_flag and is_open_access(result),
        "full_text": None,
        "full_text_stored": False,
        "abstract": None,
        "source": "europepmc",
        "fixture": bool(record.get("fixture", False)),
        "not_a_published_doi": bool(record.get("not_a_published_doi", False)),
        "europepmc": {
            "isOpenAccess": record.get("isOpenAccess"),
            "license": license_name,
            "source": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        },
        "ingest": {
            "network": "off" if not live_ingest_enabled() else "gated",
            "resolver": "europepmc",
            "standards": ["Europe PMC isOpenAccess"],
            "full_text_stored": False,
        },
    }


def _safe_doi_name(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")


def _write_metadata_only(store_dir: Path, record: Mapping[str, Any]) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    safe = strip_full_text(record)
    dest = store_dir / f"{_safe_doi_name(str(record.get('doi')))}.epmc.meta.yaml"
    dest.write_text(yaml.safe_dump(safe, sort_keys=False), encoding="utf-8")


def ingest_doi(
    doi: str,
    *,
    license_check: bool = True,
    opener: Opener | None = None,
    live: bool | None = None,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    """Resolve via Europe PMC fields. Refuse non-OA. Never write restricted text."""
    payload = fetch_search(doi, opener=opener, live=live)
    result = first_result(payload)
    if result is None:
        raise ResolutionError(f"no Europe PMC result for {doi}")
    incoming = {k: result.get(k) for k in FULL_TEXT_KEYS if result.get(k)}
    if license_check and not is_open_access(result):
        if store_dir is not None:
            for path in store_dir.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(str(v) in text for v in incoming.values()):
                    path.unlink()
        raise LicenseRefused(
            f"license not redistributable for {result.get('doi') or doi}: "
            f"{result.get('license') or 'unknown'}; full text not stored"
        )
    record = metadata_from_result(result, doi=doi)
    record["oa_permitted"] = True
    if store_dir is not None:
        _write_metadata_only(store_dir, record)
    return record
