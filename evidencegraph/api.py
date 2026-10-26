"""Public load / ingest. Same decisions as the CLI. Network off."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graph.store import ClaimStore
from ingest.resolve import resolve


def load(path: str | Path, *, store: str | Path | None = None) -> dict[str, Any]:
    root = Path(store) if store else Path.cwd() / ".evidencegraph_store"
    loaded = ClaimStore(root).load_path(Path(path))
    return {"loaded": [claim["claim_id"] for claim in loaded], "claims": loaded}


def ingest(
    doi: str,
    *,
    license_check: bool = True,
    store: str | Path | None = None,
    network: bool = False,
    source: str = "local",
    live_license: bool = False,
    live: bool | None = None,
) -> dict[str, Any]:
    return resolve(
        doi,
        license_check=license_check,
        store_dir=Path(store) if store else None,
        network=network,
        source=source,
        live_license=live_license,
        live=live,
    )
