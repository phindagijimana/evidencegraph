"""E5: extraction is not gold. Machine-extracted records cannot claim gold."""

from __future__ import annotations

from typing import Any, Mapping


def tag_machine_extracted(record: Mapping[str, Any]) -> dict[str, Any]:
    """Mark a record as machine-extracted. Always sets extraction_is_gold false."""
    tagged = dict(record)
    construction = dict(tagged.get("construction") or {})
    construction["origin"] = "machine_extracted"
    construction["extraction_is_gold"] = False
    tagged["construction"] = construction
    return tagged
