#!/usr/bin/env python3
"""Generate and validate deterministic TildenSelection evidence fixtures."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "tilden-selection.schema.json"
CASES_PATH = ROOT / "conformance" / "selection" / "selection-cases.json"


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
    return any(
        capability.get("id") == requirement["id"]
        and parameters_match(requirement.get("parameters"), capability.get("parameters"))
        for capability in capabilities
    )


def base_record(case: dict) -> dict:
    return {
        "version": "0.1",
        "selectionId": case["selectionId"],
        "target": case["targetIdentity"],
        "resolutionDigest": case["resolutionDigest"],
        "requestDigest": case["requestDigest"],
        "evaluatedAt": case["evaluatedAt"],
        "candidates": [],
    }


def generate_selection(case: dict) -> dict:
    request = case["request"]
    result = base_record(case)

    if request["target"]["canonicalIdentity"] != case["targetIdentity"]:
        result["terminal"] = "target_mismatch"
        return result

    bound_digest = request["target"].get("resolutionDigest")
    if bound_digest is not None and bound_digest != case["resolutionDigest"]:
        result["terminal"] = "resolution_mismatch"
        return result

    created = parse_time(request["createdAt"])
    expires = parse_time(request["expiresAt"])
    evaluated = parse_time(case["evaluatedAt"])
    if expires <= created or evaluated < created:
        result["terminal"] = "invalid_request"
        return result
    if evaluated >= expires:
        result["terminal"] = "expired_request"
        return result

    ordered_endpoints = sorted(
        case["endpoints"],
        key=lambda endpoint: (endpoint.get("priority", 0), endpoint["uri"]),
    )

    eligible: list[tuple[int, int, str]] = []
    evidence_by_uri: dict[str, dict] = {}

    for endpoint in ordered_endpoints:
        capabilities = endpoint.get("capabilities", [])
        priority = endpoint.get("priority", 0)
        evidence = {
            "uri": endpoint["uri"],
            "priority": priority,
            "preferenceScore": 0,
        }

        missing_required = [
            item["id"]
            for item in request["required"]
            if not capability_matches(item, capabilities)
        ]
        if missing_required:
            evidence["outcome"] = "rejected-required"
            evidence["missingRequired"] = missing_required
            result["candidates"].append(evidence)
            evidence_by_uri[endpoint["uri"]] = evidence
            continue

        matched_excluded = [
            item["id"]
            for item in request["excluded"]
            if capability_matches(item, capabilities)
        ]
        if matched_excluded:
            evidence["outcome"] = "rejected-excluded"
            evidence["matchedExcluded"] = matched_excluded
            result["candidates"].append(evidence)
            evidence_by_uri[endpoint["uri"]] = evidence
            continue

        matched_preferred = [
            item["id"]
            for item in request["preferred"]
            if capability_matches(item, capabilities)
        ]
        score = sum(
            item["weight"]
            for item in request["preferred"]
            if capability_matches(item, capabilities)
        )
        evidence["preferenceScore"] = score
        evidence["matchedPreferred"] = matched_preferred
        evidence["outcome"] = "eligible"
        result["candidates"].append(evidence)
        evidence_by_uri[endpoint["uri"]] = evidence
        eligible.append((score, priority, endpoint["uri"]))

    if not eligible:
        result["terminal"] = "no_capable_endpoint"
        return result

    eligible.sort(key=lambda item: (-item[0], item[1], item[2]))
    selected_uri = eligible[0][2]
    evidence_by_uri[selected_uri]["outcome"] = "selected"
    result["terminal"] = "selected"
    result["selectedEndpoint"] = selected_uri
    return result


def semantic_problems(record: dict) -> list[str]:
    problems: list[str] = []
    candidates = record.get("candidates", [])

    order = [(item.get("priority", 0), item["uri"]) for item in candidates]
    if order != sorted(order):
        problems.append("candidates are not in deterministic priority/URI order")

    uris = [item["uri"] for item in candidates]
    if len(uris) != len(set(uris)):
        problems.append("candidate URI appears more than once")

    selected = [item for item in candidates if item["outcome"] == "selected"]
    terminal = record.get("terminal")
    if terminal == "selected":
        if len(selected) != 1:
            problems.append("selected terminal requires exactly one selected candidate")
        elif record.get("selectedEndpoint") != selected[0]["uri"]:
            problems.append("selectedEndpoint does not match selected candidate")
    elif selected:
        problems.append("non-selected terminal must not contain selected candidate")

    for item in candidates:
        outcome = item["outcome"]
        if outcome == "rejected-required" and not item.get("missingRequired"):
            problems.append(f"{item['uri']}: required rejection lacks missingRequired")
        if outcome == "rejected-excluded" and not item.get("matchedExcluded"):
            problems.append(f"{item['uri']}: exclusion rejection lacks matchedExcluded")
        if outcome in {"eligible", "selected"} and "matchedPreferred" not in item:
            problems.append(f"{item['uri']}: eligible candidate lacks matchedPreferred")

    return problems


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    cases = load_json(CASES_PATH)["cases"]

    failed = False
    for case in cases:
        actual = generate_selection(case)
        expected = case["expected"]

        schema_errors = sorted(
            validator.iter_errors(actual), key=lambda error: list(error.path)
        )
        problems = semantic_problems(actual)

        if schema_errors or problems or actual != expected:
            failed = True
            print(f"FAIL {case['name']}")
            for error in schema_errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                print(f"  schema {location}: {error.message}")
            for problem in problems:
                print(f"  semantic: {problem}")
            if actual != expected:
                print("  generated record differs from expected fixture")
                print("  expected=" + json.dumps(expected, sort_keys=True))
                print("  actual=" + json.dumps(actual, sort_keys=True))
        else:
            print(f"PASS {case['name']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
