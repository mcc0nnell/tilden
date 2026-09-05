#!/usr/bin/env python3
"""Validate the Tilden capability registry and executable matching cases."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "capabilities-0.1.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas" / "tilden-capability-registry.schema.json"
CASES_PATH = ROOT / "conformance" / "capabilities" / "matching-cases.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def select_endpoint(required: set[str], optional: set[str], endpoints: list[dict]) -> str | None:
    candidates: list[tuple[int, str]] = []
    for endpoint in endpoints:
        capabilities = set(endpoint["capabilities"])
        if not required.issubset(capabilities):
            continue
        score = len(optional.intersection(capabilities))
        candidates.append((score, endpoint["uri"]))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][1]


def main() -> int:
    registry = load_json(REGISTRY_PATH)
    schema = load_json(REGISTRY_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(registry), key=lambda err: list(err.path))
    if errors:
        print("FAIL registry schema")
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f"  {location}: {error.message}")
        return 1

    registered = [entry["id"] for entry in registry["capabilities"]]
    if len(registered) != len(set(registered)):
        print("FAIL registry contains duplicate capability IDs")
        return 1

    allowed = set(registered)
    print(f"PASS registry ({len(allowed)} capability IDs)")

    cases = load_json(CASES_PATH)
    failed = False
    for case in cases["cases"]:
        used = set(case["required"]) | set(case["optional"])
        for endpoint in case["endpoints"]:
            used.update(endpoint["capabilities"])

        invalid = sorted(cap for cap in used if cap not in allowed and not cap.startswith("x."))
        if invalid:
            failed = True
            print(f"FAIL {case['name']}: unknown non-extension capability IDs: {', '.join(invalid)}")
            continue

        actual = select_endpoint(set(case["required"]), set(case["optional"]), case["endpoints"])
        if actual != case["expected"]:
            failed = True
            print(f"FAIL {case['name']}: expected {case['expected']!r}, got {actual!r}")
        else:
            print(f"PASS {case['name']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
