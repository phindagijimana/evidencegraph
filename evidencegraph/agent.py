"""Agent call contract. Same functions as `evidencegraph load` / ingest. Not a paper-agent."""

from __future__ import annotations

from typing import Any

from evidencegraph import ingest, load
from ingest.resolve import LicenseRefused

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
            )
        except LicenseRefused as exc:
            return {"ok": False, "reason": "license_refused", "message": str(exc)}
    raise ValueError(f"unknown tool: {name}")
