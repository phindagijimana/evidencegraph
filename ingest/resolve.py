"""License-aware ingest. DOI/PMCID → metadata or refuse. Network off by default.

Reuses Europe PMC / Crossref field names. Does not call those APIs in v0.
Never writes restricted full text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

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


class LicenseRefused(Exception):
    """License is not redistributable. Do not store full text."""


class ResolutionError(Exception):
    """DOI/PMCID could not be resolved from the local manifest."""


def normalize_license(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = text.replace("_", "-")
    text = " ".join(text.split())
    return text


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
) -> dict[str, Any]:
    """Return permitted metadata. Refuse non-OA. Never write restricted text."""
    manifest = load_manifest(manifest_path) if manifest_path or metadata is None else {}
    record = dict(metadata) if metadata is not None else lookup_manifest(doi, manifest=manifest)
    if record is None:
        raise ResolutionError(
            f"no local metadata for {doi}; network is off (Europe PMC / Crossref not called)"
        )

    incoming_text = record.get("full_text")
    record["full_text"] = None
    record["doi"] = record.get("doi") or doi
    record["source"] = record.get("source") or "local_manifest"
    record["ingest"] = {
        "network": "off",
        "resolver": "local_manifest",
        "standards": ["Europe PMC isOpenAccess", "Crossref license"],
    }

    if license_check and not is_redistributable_oa(record):
        _refuse_write(store_dir, doi, incoming_text)
        raise LicenseRefused(
            f"license not redistributable for {record.get('doi')}: "
            f"{record.get('license') or 'unknown'}; full text not stored"
        )

    record["oa_permitted"] = True
    if store_dir is not None:
        _write_metadata_only(store_dir, record)
    return record


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
    safe = {k: v for k, v in record.items() if k != "full_text"}
    safe["full_text"] = None
    dest = store_dir / f"{_safe_name(str(record.get('doi')))}.meta.yaml"
    dest.write_text(yaml.safe_dump(safe, sort_keys=False), encoding="utf-8")


def _safe_name(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")
