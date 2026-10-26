"""Optional stdio MCP transport. Calls evidencegraph.load / ingest only.

Not Paper2Agent. Not EVI. Network off. No model API.
"""

from __future__ import annotations

from evidencegraph import __version__
from evidencegraph.agent import TOOLS, call_tool
from evidencegraph.mcp_stdio import handle_message as _handle
from evidencegraph.mcp_stdio import serve

SERVER = "evidencegraph"


def handle_message(message: dict) -> dict | None:
    return _handle(
        message,
        name=SERVER,
        version=__version__,
        tools=TOOLS,
        call_tool=call_tool,
    )


def main() -> None:
    serve(name=SERVER, version=__version__, tools=TOOLS, call_tool=call_tool)


if __name__ == "__main__":
    main()
