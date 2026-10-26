"""License-aware ingest. DOI/PMCID → metadata or refuse. Network off by default.

Optional Europe PMC / Crossref clients run only when ``network=True`` and a
local OA record already exists. ``live_license=True`` may look up license
metadata when no local record exists; it still refuses non-OA.
They store metadata only. Never writes restricted full text or abstracts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PACKAGE_ROOT / "corpus" / "pilot" / "manifest.yaml"

REDISRIBUTABLE = frozenset(
    {
        "cc0",
        "cc-by",
        "cc-by-4.0",
        "cc-by-sa",
        "cc-by-sa-4.0",
        "cc by",
        "cc by 4.0",
        "public-domain",
        "publicdomain",
    }
)

FULL_TEXT_KEYS = (
    "full_text",
    "fullText",
    "fullTextXml",
    "fullTextXML",
    "fullTextHtml",
    "inTextAbstract",
    "abstract",
    "abstractText",
)

OPTIONAL_SOURCES = frozenset({"europepmc", "crossref"})
Opener = Callable[[str], str]


class LicenseRefused(Exception):
    """License is not redistributable. Do not store full text."""


class ResolutionError(Exception):
    """DOI/PMCID could not be resolved from the local manifest."""


class NetworkScrapeRefused(Exception):
    """--network without a local OA record. Do not scrape restricted text."""


def normalize_license(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = text.replace("_", "-")
    text = " ".join(text.split())
    return text


def strip_restricted_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    """Drop full text, abstracts, and PDF/link lists. Metadata only."""
    cleaned = {k: v for k, v in record.items() if k not in FULL_TEXT_KEYS}
    for key in FULL_TEXT_KEYS:
        cleaned[key] = None
    cleaned.pop("fullTextUrlList", None)
    cleaned.pop("link", None)
    cleaned.pop("reference", None)
    cleaned["full_text_stored"] = False
    return cleaned


def is_redistributable_oa(record: Mapping[str, Any]) -> bool:
    if record.get("is_oa") is False or record.get("redistributable") is False:
        return False
    license_name = normalize_license(record.get("license"))
    if not license_name:
        epmc = record.get("europepmc") or {}
        if str(epmc.get("isOpenAccess", "")).upper() == "N":
            return False
        license_name = normalize_license(epmc.get("license"))
    if not license_name:
        return False
    compact = license_name.replace(" ", "-")
    return license_name in REDISRIBUTABLE or compact in REDISRIBUTABLE


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or DEFAULT_MANIFEST
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return data or {}


def lookup_manifest(
    doi: str, *, manifest: Mapping[str, Any] | None = None
) -> dict[str, Any] | None:
    key = doi.strip()
    papers = (manifest or load_manifest()).get("papers") or []
    for paper in papers:
        if str(paper.get("doi", "")).strip() == key:
            return dict(paper)
        if str(paper.get("paper_id", "")).strip() == key:
            return dict(paper)
        if str(paper.get("pmcid", "")).strip() == key:
            return dict(paper)
    return None


def resolve(
    doi: str,
    *,
    license_check: bool = True,
    metadata: Mapping[str, Any] | None = None,
    manifest_path: Path | None = None,
    store_dir: Path | None = None,
    network: bool = False,
    source: str = "local",
    opener: Opener | None = None,
    live: bool | None = None,
    live_license: bool = False,
) -> dict[str, Any]:
    """Return permitted metadata. Refuse non-OA. Never write restricted text.

    Network is off by default. ``network=True`` still refuses unless a local
    OA record exists. ``live_license=True`` may look up Crossref / Europe PMC
    *license metadata only* when no local record exists; it still refuses
    non-OA and never stores full text. Optional ``source`` europepmc|crossref
    may attach metadata from those clients; full text is never stored.
    """
    chosen = (source or "local").strip().lower()
    if chosen not in {"local", "europepmc", "crossref"}:
        raise ResolutionError(f"unknown ingest source: {source}")

    manifest = load_manifest(manifest_path) if manifest_path or metadata is None else {}
    record = dict(metadata) if metadata is not None else lookup_manifest(doi, manifest=manifest)
    if record is None:
        if live_license:
            return _live_license_lookup(
                doi,
                license_check=license_check,
                source=chosen,
                opener=opener,
                live=live,
                store_dir=store_dir,
            )
        if network:
            raise NetworkScrapeRefused(
                f"no local OA record for {doi}; refuse scrape; "
                "restricted full text not fetched"
            )
        raise ResolutionError(
            f"no local metadata for {doi}; network is off (Europe PMC / Crossref not called)"
        )

    incoming_text = record.get("full_text") or record.get("abstract")
    record = strip_restricted_payload(record)
    record["doi"] = record.get("doi") or doi
    record["source"] = record.get("source") or "local_manifest"
    record["ingest"] = {
        "network": "requested_local_only" if network else "off",
        "resolver": "local_manifest",
        "optional_client": chosen if chosen in OPTIONAL_SOURCES else None,
        "scrape": False,
        "full_text_stored": False,
        "standards": ["Europe PMC isOpenAccess", "Crossref license"],
    }

    if license_check and not is_redistributable_oa(record):
        _refuse_write(store_dir, doi, incoming_text)
        raise LicenseRefused(
            f"license not redistributable for {record.get('doi')}: "
            f"{record.get('license') or 'unknown'}; full text not stored"
        )

    if network and chosen in OPTIONAL_SOURCES:
        remote, client_url = _optional_client_metadata(
            doi, chosen, opener=opener, live=live
        )
        record["ingest"]["client_url"] = client_url
        if remote:
            record = _merge_metadata_only(record, remote)
            record["ingest"]["resolver"] = f"local_manifest+{chosen}"
        record["ingest"]["optional_client"] = chosen
        record["ingest"]["network"] = "requested_local_only"
        record["ingest"]["scrape"] = False
        record = strip_restricted_payload(record)

    record["oa_permitted"] = True
    record["full_text_stored"] = False
    if store_dir is not None:
        _write_metadata_only(store_dir, record)
    return record


def _live_license_lookup(
    doi: str,
    *,
    license_check: bool,
    source: str,
    opener: Opener | None,
    live: bool | None,
    store_dir: Path | None,
) -> dict[str, Any]:
    """Metadata-only license check. Never scrapes or stores full text."""
    from urllib.error import HTTPError, URLError

    chosen = source if source in OPTIONAL_SOURCES else "crossref"
    if chosen == "europepmc":
        from ingest.europepmc import (
            NetworkDisabled,
            build_search_url,
            ingest_doi,
            live_ingest_enabled,
        )

        client_url = build_search_url(doi)
    else:
        from ingest.crossref import (
            NetworkDisabled,
            build_works_url,
            ingest_doi,
            live_ingest_enabled,
        )

        client_url = build_works_url(doi)

    if opener is None:
        allowed = live if live is not None else live_ingest_enabled()
        if not allowed:
            raise ResolutionError(
                f"live license check network is off for {doi}; "
                f"set EG_LIVE_INGEST=1 for a metadata-only Crossref / Europe PMC call"
            )

    try:
        record = ingest_doi(
            doi,
            license_check=license_check,
            opener=opener,
            live=True if live is None else live,
            store_dir=store_dir,
        )
    except NetworkDisabled as exc:
        raise ResolutionError(str(exc)) from exc
    except HTTPError as exc:
        raise ResolutionError(
            f"no Crossref/Europe PMC license record for {doi}; full text not stored"
        ) from exc
    except URLError as exc:
        raise ResolutionError(
            f"live license check failed for {doi}; full text not stored"
        ) from exc

    record = strip_restricted_payload(record)
    record["doi"] = record.get("doi") or doi
    record["ingest"] = {
        "network": "live_license",
        "resolver": chosen,
        "optional_client": chosen,
        "scrape": False,
        "full_text_stored": False,
        "client_url": client_url,
        "standards": ["Europe PMC isOpenAccess", "Crossref license"],
    }
    record["oa_permitted"] = True
    record["full_text_stored"] = False
    if store_dir is not None:
        _write_metadata_only(store_dir, record)
    return record


def _optional_client_metadata(
    doi: str,
    source: str,
    *,
    opener: Opener | None,
    live: bool | None,
) -> tuple[dict[str, Any] | None, str]:
    """Call an optional client only when mocked or live-gated. Never scrape."""
    if source == "europepmc":
        from ingest.europepmc import build_search_url, ingest_doi, live_ingest_enabled

        url = build_search_url(doi)
        should_call = opener is not None or (
            live if live is not None else live_ingest_enabled()
        )
        if should_call:
            return ingest_doi(doi, opener=opener, live=live, store_dir=None), url
        return None, url
    if source == "crossref":
        from ingest.crossref import build_works_url, ingest_doi, live_ingest_enabled

        url = build_works_url(doi)
        should_call = opener is not None or (
            live if live is not None else live_ingest_enabled()
        )
        if should_call:
            return ingest_doi(doi, opener=opener, live=live, store_dir=None), url
        return None, url
    return None, ""


def _merge_metadata_only(
    local: Mapping[str, Any], remote: Mapping[str, Any]
) -> dict[str, Any]:
    merged = strip_restricted_payload(local)
    remote_clean = strip_restricted_payload(remote)
    for key in ("title", "license", "pmcid", "publisher", "container_title", "issued"):
        if remote_clean.get(key) and not merged.get(key):
            merged[key] = remote_clean[key]
    for block in ("crossref", "europepmc"):
        if remote_clean.get(block):
            merged[block] = remote_clean[block]
    if remote_clean.get("source"):
        merged["remote_source"] = remote_clean["source"]
    return strip_restricted_payload(merged)


def _refuse_write(store_dir: Path | None, doi: str, incoming_text: Any) -> None:
    if incoming_text in (None, ""):
        return
    if store_dir is None:
        return
    # Must not persist restricted payload even if the caller supplied it.
    for path in store_dir.rglob("*"):
        if path.is_file() and str(incoming_text) in path.read_text(encoding="utf-8", errors="ignore"):
            path.unlink()


def _write_metadata_only(store_dir: Path, record: Mapping[str, Any]) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    safe = strip_restricted_payload(record)
    dest = store_dir / f"{_safe_name(str(record.get('doi')))}.meta.yaml"
    dest.write_text(yaml.safe_dump(safe, sort_keys=False), encoding="utf-8")


def _safe_name(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")
