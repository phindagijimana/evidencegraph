"""Public import, agent tool, optional MCP. Network off. No model API."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from evidencegraph import ingest, load
from evidencegraph.agent import TOOLS, call_tool
from evidencegraph.mcp import handle_message
from ingest.resolve import LicenseRefused

ROOT = Path(__file__).resolve().parents[1]
ITEM = ROOT / "evaluation/items/I003.yaml"


def test_public_load_and_ingest(tmp_path: Path) -> None:
    os.environ.pop("OPENAI_API_KEY", None)
    loaded = load(ITEM, store=tmp_path)
    assert "C-I003-A" in loaded["loaded"]
    with pytest.raises(LicenseRefused):
        ingest("10.9999/restricted-mock", license_check=True)


def test_agent_tool_matches_load(tmp_path: Path) -> None:
    via = call_tool("load", {"path": str(ITEM), "store": str(tmp_path)})
    assert "C-I003-A" in via["loaded"]
    refused = call_tool("ingest", {"doi": "10.9999/restricted-mock"})
    assert refused["reason"] == "license_refused"
    assert {tool["name"] for tool in TOOLS} == {"load", "ingest"}


def test_mcp_tools_call_load(tmp_path: Path) -> None:
    listed = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert {tool["name"] for tool in listed["result"]["tools"]} == {"load", "ingest"}
    called = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "load",
                "arguments": {"path": str(ITEM), "store": str(tmp_path)},
            },
        }
    )
    assert called["result"]["isError"] is False
    assert "C-I003-A" in called["result"]["content"][0]["text"]
