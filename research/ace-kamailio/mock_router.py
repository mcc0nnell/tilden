#!/usr/bin/env python3
"""Deterministic offline model of the useful ACE Kamailio routing donor states.

This is not a Kamailio emulator. It preserves only the control-flow concepts
used by Tilden research: source-role separation, backend selection, registration
forwarding, and explicit route exhaustion.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
VECTORS = ROOT / "mock-vectors.json"


def select_destination(destinations: list[dict], cursor: int) -> tuple[str | None, int]:
    if not destinations:
        return None, 0
    count = len(destinations)
    start = cursor % count
    for offset in range(count):
        index = (start + offset) % count
        destination = destinations[index]
        if destination.get("healthy") is True:
            return destination["uri"], (index + 1) % count
    return None, start


def route(case: dict) -> dict:
    method = case["method"].upper()
    role = case["sourceRole"]
    cursor = int(case.get("cursor", 0))
    destinations = case.get("destinations", [])

    if role == "media_server":
        return {"action": "inside_route", "selected": None, "nextCursor": cursor}

    if method == "INVITE":
        selected, next_cursor = select_destination(destinations, cursor)
        if selected is None:
            return {"action": "route_unavailable", "selected": None, "nextCursor": next_cursor}
        return {
            "action": "dispatch_media_server",
            "selected": selected,
            "nextCursor": next_cursor,
        }

    if method == "REGISTER":
        selected, next_cursor = select_destination(destinations, cursor)
        if selected is None:
            return {"action": "route_unavailable", "selected": None, "nextCursor": next_cursor}
        return {
            "action": "forward_registration",
            "selected": selected,
            "nextCursor": next_cursor,
        }

    return {"action": "direct_policy_path", "selected": None, "nextCursor": cursor}


def require_example_uri(uri: str) -> None:
    parsed = urlparse(uri)
    # urlparse does not treat sip: as a hostname-bearing network URL, so inspect
    # the scheme-specific part explicitly.
    if parsed.scheme != "sip":
        raise AssertionError(f"mock endpoint must use sip: URI: {uri}")
    authority = parsed.path.rsplit("@", 1)[-1].split(";", 1)[0]
    host = authority.rsplit(":", 1)[0] if ":" in authority else authority
    if not host.endswith(".example"):
        raise AssertionError(f"mock endpoint escaped reserved .example space: {uri}")


def main() -> int:
    document = json.loads(VECTORS.read_text(encoding="utf-8"))
    boundary = document["claimBoundary"]
    if any(boundary.values()):
        raise AssertionError("donor mock claim boundary must remain entirely false")

    vectors = document["vectors"]
    seen: set[str] = set()
    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen:
            raise AssertionError(f"duplicate vector id: {vector_id}")
        seen.add(vector_id)

        for destination in vector["input"].get("destinations", []):
            require_example_uri(destination["uri"])

        actual = route(vector["input"])
        expected = vector["expected"]
        if actual != expected:
            raise AssertionError(
                f"{vector_id}: expected {expected!r}, observed {actual!r}"
            )
        print(f"PASS {vector_id}: {actual['action']}")

    print(f"validated {len(vectors)} ACE Kamailio donor vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
