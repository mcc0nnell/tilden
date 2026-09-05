#!/usr/bin/env python3
"""Validate Tilden example objects against the draft JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "tilden-resolution.schema.json"
EXAMPLES_DIR = ROOT / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    examples = sorted(EXAMPLES_DIR.glob("*.json"))
    if not examples:
        raise SystemExit("no JSON examples found")

    failed = False
    for path in examples:
        instance = load_json(path)
        errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.path))
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
