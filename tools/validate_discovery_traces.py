#!/usr/bin/env python3
"""Validate Tilden discovery evidence fixtures against the draft schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "tilden-discovery-trace.schema.json"
VALID_DIR = ROOT / "conformance" / "discovery" / "valid"
INVALID_DIR = ROOT / "conformance" / "discovery" / "invalid"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    validator = Draft202012Validator(load_json(SCHEMA_PATH), format_checker=FormatChecker())
    valid = sorted(VALID_DIR.glob("*.json"))
    invalid = sorted(INVALID_DIR.glob("*.json"))
    if not valid or not invalid:
        raise SystemExit("discovery conformance requires valid and invalid fixtures")

    failed = False

    for path in valid:
        errors = list(validator.iter_errors(load_json(path)))
        if errors:
            failed = True
            print(f"FAIL expected-valid {path.relative_to(ROOT)}")
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                print(f"  {location}: {error.message}")
        else:
            print(f"PASS expected-valid {path.relative_to(ROOT)}")

    for path in invalid:
        errors = list(validator.iter_errors(load_json(path)))
        if errors:
            print(f"PASS expected-invalid {path.relative_to(ROOT)}")
        else:
            failed = True
            print(f"FAIL expected-invalid accepted {path.relative_to(ROOT)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
