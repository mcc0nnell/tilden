#!/usr/bin/env python3
"""Deterministic state-machine mock derived from the ACE Direct iTRS donor.

This module never performs DNS, SIP, or production iTRS access. It consumes
scripted observations and verifies that Tilden can preserve the donor's useful
resolution stages without importing its shell implementation or claiming that
legacy results are current.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

DEFAULT_VECTORS = Path(__file__).with_name("mock-vectors.json")


def normalize_nanp(number: str) -> str:
    """Apply only the NANP-oriented normalization evidenced by the donor."""
    if number.startswith("+1"):
        number = number[2:]
    elif len(number) == 11 and number.startswith("1"):
        number = number[1:]

    if len(number) != 10 or not number.isdigit():
        raise ValueError("ACE donor profile requires a ten-digit NANP number after normalization")
    return number


def enum_query(number: str) -> str:
    normalized = normalize_nanp(number)
    return ".".join(reversed(normalized)) + ".1.itrs.us"


def evaluate(vector: dict[str, Any]) -> dict[str, Any]:
    mode = vector["mode"]
    if mode not in {"simple", "full"}:
        raise ValueError(f"unsupported donor mode: {mode}")

    normalized = normalize_nanp(vector["input"]["number"])
    observations = vector["observations"]
    discovery_target = observations.get("e2uSip")

    base: dict[str, Any] = {
        "normalizedNumber": normalized,
        "enumQuery": enum_query(normalized),
        "discoveryTarget": discovery_target,
        "status": "not_found",
        "route": None,
        "fallbackAttempted": False,
    }

    if not discovery_target:
        return base

    if mode == "simple":
        base["status"] = "found"
        return base

    transport_target = observations.get("transportNaptr")
    if not transport_target:
        # The historical shell attempts a port-5060 fallback. This mock records
        # that policy fact but deliberately does not invent a successful route.
        base["status"] = "transport_unavailable"
        base["fallbackAttempted"] = True
        return base

    srv = observations.get("srv")
    if not srv:
        base["status"] = "route_unavailable"
        return base

    host = srv["host"]
    provider_map = observations.get("providerMap", {})
    base["status"] = "routable"
    base["route"] = {
        "host": host,
        "port": int(srv["port"]),
        "provider": provider_map.get(host),
    }
    return base


def validate(path: Path) -> int:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != "tilden.research.ace-itrs.v1":
        raise ValueError("unexpected ACE donor vector format")

    failures = 0
    for vector in document["vectors"]:
        actual = evaluate(vector)
        expected = vector["expected"]
        if actual != expected:
            failures += 1
            print(f"FAIL {vector['id']}", file=sys.stderr)
            print(json.dumps({"expected": expected, "actual": actual}, indent=2), file=sys.stderr)
        else:
            print(f"PASS {vector['id']}")
    return failures


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VECTORS
    failures = validate(path)
    if failures:
        print(f"{failures} ACE iTRS donor vector(s) failed", file=sys.stderr)
        return 1
    print("ACE iTRS donor vectors passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
