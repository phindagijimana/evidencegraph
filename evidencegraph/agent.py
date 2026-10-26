"""Agent call contract. Same functions as `evidencegraph load` / ingest. Not a paper-agent."""

from __future__ import annotations

from typing import Any

from evidencegraph import ingest, load
from ingest.resolve import LicenseRefused, NetworkScrapeRefused

TOOLS: list[dict[str, Any]] = [
    {
        "name": "load",
        "description": (
            "Load a scoped claim–evidence item. "
            "Incomparable atlas or cohort is Qualifies, not Contradicts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to claim or gold-item YAML"},
                "store": {"type": "string", "description": "Optional store directory"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "ingest",
        "description": (
            "Resolve a DOI from the local manifest. "
            "Refuses non-redistributable licenses. Network off. No restricted full text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "doi": {"type": "string"},
                "license_check": {"type": "boolean", "default": True},
                "store": {"type": "string"},
                "network": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Request network. Still refuses without a local OA "
                        "record. Optional Europe PMC / Crossref store "
                        "metadata only. Never scrapes restricted full text."
                    ),
                },
                "source": {
                    "type": "string",
                    "enum": ["local", "europepmc", "crossref"],
                    "default": "local",
                },
                "live_license": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Metadata-only Crossref / Europe PMC license check "
                        "when no local record exists. Refuses non-OA. "
                        "Never stores full text."
                    ),
                },
            },
            "required": ["doi"],
        },
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "load":
        return load(arguments["path"], store=arguments.get("store"))
    if name == "ingest":
        try:
            return ingest(
                arguments["doi"],
                license_check=bool(arguments.get("license_check", True)),
                store=arguments.get("store"),
                network=bool(arguments.get("network", False)),
                source=str(arguments.get("source") or "local"),
                live_license=bool(arguments.get("live_license", False)),
            )
        except LicenseRefused as exc:
            return {"ok": False, "reason": "license_refused", "message": str(exc)}
        except NetworkScrapeRefused as exc:
            return {"ok": False, "reason": "scrape_refused", "message": str(exc)}
    raise ValueError(f"unknown tool: {name}")
