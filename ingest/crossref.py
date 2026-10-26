"""Crossref ingest client. Builds the works URL. Default network off.

Reuses Crossref license URL fields. Does not replace ingest/resolve.py.
A live HTTP call runs only when EG_LIVE_INGEST=1.
Never stores restricted full text, abstracts, or PDF bytes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from ingest.resolve import (
    FULL_TEXT_KEYS,
    LicenseRefused,
    ResolutionError,
    is_redistributable_oa,
    strip_restricted_payload,
)

CROSSREF_WORKS = "https://api.crossref.org/works"
LIVE_ENV = "EG_LIVE_INGEST"

Opener = Callable[[str], str]


class NetworkDisabled(Exception):
    """Network is off. Crossref is not called unless EG_LIVE_INGEST=1."""


def live_ingest_enabled() -> bool:
    return os.environ.get(LIVE_ENV, "") == "1"


def build_works_url(doi: str) -> str:
    """Construct the Crossref works URL. Does not perform I/O."""
    key = (doi or "").strip()
    if not key:
        raise ResolutionError("DOI is required to build a Crossref URL")
    return f"{CROSSREF_WORKS}/{quote(key, safe='')}"


def map_license_url(url: str) -> str:
    text = (url or "").strip().lower().rstrip("/")
    text = text.replace("http://", "https://")
    if "creativecommons.org/publicdomain/zero" in text:
        return "cc0"
    if "creativecommons.org/licenses/by-sa/4.0" in text:
        return "cc-by-sa-4.0"
    if "creativecommons.org/licenses/by/4.0" in text:
        return "cc-by-4.0"
    if "creativecommons.org/licenses/by-sa" in text:
        return "cc-by-sa"
    if "creativecommons.org/licenses/by" in text:
        return "cc-by"
    return ""


def license_urls_from_message(message: Mapping[str, Any] | None) -> list[str]:
    if not message:
        return []
    urls: list[str] = []
    for entry in message.get("license") or []:
        if not isinstance(entry, Mapping):
            continue
        url = entry.get("URL") or entry.get("url")
        if url:
            urls.append(str(url))
    return urls


def first_mapped_license(urls: list[str]) -> str:
    for url in urls:
        mapped = map_license_url(url)
        if mapped:
            return mapped
    return ""


def parse_works_payload(raw: str | Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(raw) if isinstance(raw, Mapping) else json.loads(raw)
    message = payload.get("message")
    if not isinstance(message, Mapping):
        raise ResolutionError("no Crossref works message")
    return dict(message)


def is_open_access(message: Mapping[str, Any] | None) -> bool:
    if not message:
        return False
    mapped = first_mapped_license(license_urls_from_message(message))
    if not mapped:
        return False
    record = {
        "doi": message.get("DOI"),
        "license": mapped,
        "is_oa": True,
        "crossref": {"license_url": license_urls_from_message(message)[0]},
    }
    return is_redistributable_oa(record)


def _title(message: Mapping[str, Any]) -> str | None:
    titles = message.get("title") or []
    if isinstance(titles, list) and titles:
        return str(titles[0])
    if isinstance(titles, str) and titles:
        return titles
    return None


def _container(message: Mapping[str, Any]) -> str | None:
    containers = message.get("container-title") or []
    if isinstance(containers, list) and containers:
        return str(containers[0])
    if isinstance(containers, str) and containers:
        return containers
    return None


def _issued(message: Mapping[str, Any]) -> str | None:
    parts = ((message.get("issued") or {}).get("date-parts") or [[]])[0]
    if not parts:
        return None
    return "-".join(f"{int(p):02d}" if i else str(int(p)) for i, p in enumerate(parts))


def _http_get(url: str, *, timeout: float = 20.0) -> str:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "evidencegraph/0.1 "
                "(https://github.com/phindagijimana/evidencegraph; metadata-only)"
            ),
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_works(
    doi: str,
    *,
    opener: Opener | None = None,
    live: bool | None = None,
) -> dict[str, Any]:
    """Return a parsed Crossref works message. Network off unless gated or mocked."""
    url = build_works_url(doi)
    allowed = live_ingest_enabled() if live is None else bool(live)
    if opener is not None:
        return parse_works_payload(opener(url))
    if not allowed:
        raise NetworkDisabled(
            f"network is off; Crossref not called for {doi}. "
            f"Set {LIVE_ENV}=1 for a live call"
        )
    return parse_works_payload(_http_get(url))


def metadata_from_message(message: Mapping[str, Any], *, doi: str) -> dict[str, Any]:
    cleaned = strip_restricted_payload(message)
    urls = license_urls_from_message(message)
    mapped = first_mapped_license(urls)
    oa = bool(mapped) and is_open_access(message)
    return {
        "doi": cleaned.get("DOI") or message.get("DOI") or doi,
        "title": _title(message),
        "license": mapped or None,
        "is_oa": oa,
        "redistributable": oa,
        "publisher": message.get("publisher"),
        "container_title": _container(message),
        "issued": _issued(message),
        "full_text": None,
        "full_text_stored": False,
        "abstract": None,
        "source": "crossref",
        "fixture": bool(message.get("fixture", False)),
        "not_a_published_doi": bool(message.get("not_a_published_doi", False)),
        "crossref": {
            "license_url": urls[0] if urls else None,
            "publisher": message.get("publisher"),
            "container_title": _container(message),
            "issued": _issued(message),
            "type": message.get("type"),
            "source": CROSSREF_WORKS,
        },
        "ingest": {
            "network": "off" if not live_ingest_enabled() else "gated",
            "resolver": "crossref",
            "standards": ["Crossref license"],
            "full_text_stored": False,
            "scrape": False,
        },
    }


def _safe_doi_name(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")


def _write_metadata_only(store_dir: Path, record: Mapping[str, Any]) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    safe = strip_restricted_payload(record)
    dest = store_dir / f"{_safe_doi_name(str(record.get('doi')))}.crossref.meta.yaml"
    dest.write_text(yaml.safe_dump(safe, sort_keys=False), encoding="utf-8")


def ingest_doi(
    doi: str,
    *,
    license_check: bool = True,
    opener: Opener | None = None,
    live: bool | None = None,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    """Resolve via Crossref license fields. Refuse non-OA. Never write restricted text."""
    message = fetch_works(doi, opener=opener, live=live)
    incoming = {k: message.get(k) for k in FULL_TEXT_KEYS if message.get(k)}
    if license_check and not is_open_access(message):
        if store_dir is not None:
            for path in store_dir.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(str(v) in text for v in incoming.values()):
                    path.unlink()
        raise LicenseRefused(
            f"license not redistributable for {message.get('DOI') or doi}: "
            f"{first_mapped_license(license_urls_from_message(message)) or 'unknown'}; "
            "full text not stored"
        )
    record = metadata_from_message(message, doi=doi)
    record["oa_permitted"] = True
    if store_dir is not None:
        _write_metadata_only(store_dir, record)
    return record
