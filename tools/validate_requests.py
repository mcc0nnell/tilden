#!/usr/bin/env python3
"""Validate TildenRequest fixtures and deterministic endpoint selection."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "tilden-request.schema.json"
VALID_DIR = ROOT / "conformance" / "request" / "valid"
CASES_PATH = ROOT / "conformance" / "request" / "selection-cases.json"
REGISTRY_PATH = ROOT / "registry" / "capabilities-0.1.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parameters_match(requested: dict | None, asserted: dict | None) -> bool:
    if not requested:
        return True
    if not asserted:
        return False

    for key, wanted in requested.items():
        if key not in asserted:
            return False
        actual = asserted[key]

        if isinstance(wanted, dict):
            return False
        if isinstance(wanted, list):
            if not isinstance(actual, list):
                return False
            if not any(item in actual for item in wanted):
                return False
        elif actual != wanted:
            return False

    return True


def capability_matches(requirement: dict, capabilities: list[dict]) -> bool:
    for capability in capabilities:
        if capability.get("id") != requirement["id"]:
            continue
        if parameters_match(requirement.get("parameters"), capability.get("parameters")):
            return True
    return False


def select_endpoint(request: dict, target_identity: str, now: datetime, endpoints: list[dict]):
    if request["target"]["canonicalIdentity"] != target_identity:
        return None, "target_mismatch"

    created = parse_time(request["createdAt"])
    expires = parse_time(request["expiresAt"])
    if expires <= created:
        return None, "invalid_request"
    if now < created:
        return None, "invalid_request"
    if now >= expires:
        return None, "expired_request"

    candidates: list[tuple[int, int, str]] = []
    for endpoint in endpoints:
        capabilities = endpoint.get("capabilities", [])

        if not all(capability_matches(item, capabilities) for item in request["required"]):
            continue
        if any(capability_matches(item, capabilities) for item in request["excluded"]):
            continue

        score = sum(
            item["weight"]
            for item in request["preferred"]
            if capability_matches(item, capabilities)
        )
        priority = endpoint.get("priority", 0)
        candidates.append((score, priority, endpoint["uri"]))

    if not candidates:
        return None, "no_capable_endpoint"

    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    return candidates[0][2], None


def validate_request(instance: dict, validator, allowed: set[str]) -> list[str]:
    problems: list[str] = []
    for error in sorted(validator.iter_errors(instance), key=lambda err: list(err.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        problems.append(f"{location}: {error.message}")

    used = {
        item["id"]
        for section in ("required", "preferred", "excluded")
        for item in instance.get(section, [])
        if isinstance(item, dict) and "id" in item
    }
    unknown = sorted(cap for cap in used if cap not in allowed and not cap.startswith("x."))
    if unknown:
        problems.append(f"unknown non-extension capability IDs: {', '.join(unknown)}")

    try:
        if parse_time(instance["expiresAt"]) <= parse_time(instance["createdAt"]):
            problems.append("expiresAt must be later than createdAt")
    except (KeyError, ValueError):
        pass

    return problems


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    registry = load_json(REGISTRY_PATH)
    allowed = {entry["id"] for entry in registry["capabilities"]}

    failed = False

    fixtures = sorted(VALID_DIR.glob("*.json"))
    if not fixtures:
        raise SystemExit("no valid request fixtures found")

    for path in fixtures:
        problems = validate_request(load_json(path), validator, allowed)
        if problems:
            failed = True
            print(f"FAIL {path.relative_to(ROOT)}")
            for problem in problems:
                print(f"  {problem}")
        else:
            print(f"PASS {path.relative_to(ROOT)}")

    cases = load_json(CASES_PATH)["cases"]
    for case in cases:
        request = case["request"]
        problems = validate_request(request, validator, allowed)
        if problems:
            failed = True
            print(f"FAIL {case['name']}: invalid request fixture")
            for problem in problems:
                print(f"  {problem}")
            continue

        actual, failure = select_endpoint(
            request,
            case["targetIdentity"],
            parse_time(case["now"]),
            case["endpoints"],
        )
        expected_failure = case.get("expectedFailure")
        if actual != case.get("expected") or failure != expected_failure:
            failed = True
            print(
                f"FAIL {case['name']}: expected endpoint={case.get('expected')!r}, "
                f"failure={expected_failure!r}; got endpoint={actual!r}, failure={failure!r}"
            )
        else:
            print(f"PASS {case['name']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
