#!/usr/bin/env python3
"""Validate Tilden discovery evidence fixtures against the draft schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "tilden-discovery-trace.schema.json"
FIXTURES_DIR = ROOT / "conformance" / "discovery" / "valid"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    validator = Draft202012Validator(load_json(SCHEMA_PATH), format_checker=FormatChecker())
    fixtures = sorted(FIXTURES_DIR.glob("*.json"))
    if not fixtures:
        raise SystemExit("no discovery fixtures found")

    failed = False
    for path in fixtures:
        errors = sorted(validator.iter_errors(load_json(path)), key=lambda err: list(err.path))
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(ROOT)}")
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                print(f"  {location}: {error.message}")
        else:
            print(f"PASS {path.relative_to(ROOT)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
