from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(value: Any, path: str | None) -> None:
    text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def canonical_bytes(value: Any) -> bytes:
    """Reference-only deterministic JSON encoding; not yet a normative Tilden digest profile."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
            if not isinstance(actual, list) or not any(item in actual for item in wanted):
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


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if value.isdigit():
        return int(value)
    return value


def parse_capability_spec(text: str, *, preferred: bool = False) -> dict:
    weight = 50
    body = text
    if preferred and "@" in body:
        body, weight_text = body.rsplit("@", 1)
        weight = int(weight_text)
        if not 1 <= weight <= 100:
            raise ValueError("preference weight must be 1..100")

    if ":" in body:
        cap_id, raw_params = body.split(":", 1)
    else:
        cap_id, raw_params = body, ""

    result: dict[str, Any] = {"id": cap_id}
    params: dict[str, Any] = {}
    if raw_params:
        for item in raw_params.split(";"):
            if "=" not in item:
                raise ValueError(f"invalid capability parameter: {item}")
            key, raw_value = item.split("=", 1)
            values = [parse_scalar(value) for value in raw_value.split(",")]
            params[key] = values if len(values) > 1 or key.endswith("s") else values[0]
    if params:
        result["parameters"] = params
    if preferred:
        result["weight"] = weight
    return result


def validate_resolution_shape(resolution: dict) -> None:
    required = {"version", "canonicalIdentity", "authority", "endpoints", "capabilities", "trust", "expiresAt"}
    missing = sorted(required - set(resolution))
    if missing:
        raise ValueError("resolution missing required fields: " + ", ".join(missing))
    if resolution["version"] != "0.1":
        raise ValueError("unsupported resolution version")
    if not isinstance(resolution["endpoints"], list) or not resolution["endpoints"]:
        raise ValueError("resolution must contain at least one endpoint")


def cmd_resolve(args: argparse.Namespace) -> int:
    directory = load_json(args.directory)
    records = directory.get("records", {}) if isinstance(directory, dict) else {}
    identifier = args.identifier.strip()
    resolution = records.get(identifier)
    if resolution is None:
        print(f"tilden: identifier not found: {identifier}", file=sys.stderr)
        return 2
    validate_resolution_shape(resolution)
    if resolution["canonicalIdentity"] != identifier:
        raise ValueError("directory record canonicalIdentity does not match lookup key")
    write_json(resolution, args.out)
    return 0


def cmd_request(args: argparse.Namespace) -> int:
    now = datetime.now(timezone.utc)
    target: dict[str, str] = {"canonicalIdentity": args.identifier.strip()}
    if args.resolution:
        resolution = load_json(args.resolution)
        validate_resolution_shape(resolution)
        if resolution["canonicalIdentity"] != target["canonicalIdentity"]:
            raise ValueError("resolution canonical identity does not match request target")
        target["resolutionDigest"] = digest_json(resolution)

    request = {
        "version": "0.1",
        "scope": "local-selection",
        "requestId": "req-" + secrets.token_urlsafe(12),
        "nonce": secrets.token_urlsafe(24),
        "target": target,
        "required": [parse_capability_spec(value) for value in args.require],
        "preferred": [parse_capability_spec(value, preferred=True) for value in args.prefer],
        "excluded": [parse_capability_spec(value) for value in args.exclude],
        "createdAt": isoformat_z(now),
        "expiresAt": isoformat_z(now + timedelta(seconds=args.ttl)),
    }
    write_json(request, args.out)
    return 0


def generate_selection(resolution: dict, request: dict, evaluated: datetime) -> dict:
    validate_resolution_shape(resolution)
    resolution_digest = digest_json(resolution)
    request_digest = digest_json(request)
    evaluated_at = isoformat_z(evaluated)
    seed = f"{resolution_digest}|{request_digest}|{evaluated_at}".encode("utf-8")
    selection_id = "sel-" + hashlib.sha256(seed).hexdigest()[:20]

    result: dict[str, Any] = {
        "version": "0.1",
        "selectionId": selection_id,
        "target": resolution["canonicalIdentity"],
        "resolutionDigest": resolution_digest,
        "requestDigest": request_digest,
        "evaluatedAt": evaluated_at,
        "candidates": [],
    }

    if request.get("target", {}).get("canonicalIdentity") != resolution["canonicalIdentity"]:
        result["terminal"] = "target_mismatch"
        return result

    bound_digest = request.get("target", {}).get("resolutionDigest")
    if bound_digest is not None and bound_digest != resolution_digest:
        result["terminal"] = "resolution_mismatch"
        return result

    try:
        created = parse_time(request["createdAt"])
        expires = parse_time(request["expiresAt"])
    except (KeyError, ValueError, TypeError):
        result["terminal"] = "invalid_request"
        return result

    if expires <= created or evaluated < created:
        result["terminal"] = "invalid_request"
        return result
    if evaluated >= expires:
        result["terminal"] = "expired_request"
        return result

    required = request.get("required", [])
    preferred = request.get("preferred", [])
    excluded = request.get("excluded", [])

    ordered_endpoints = sorted(
        resolution["endpoints"],
        key=lambda endpoint: (endpoint.get("priority", 0), endpoint["uri"]),
    )
    eligible: list[tuple[int, int, str]] = []
    evidence_by_uri: dict[str, dict] = {}

    for endpoint in ordered_endpoints:
        capabilities = endpoint.get("capabilities", [])
        priority = endpoint.get("priority", 0)
        evidence: dict[str, Any] = {
            "uri": endpoint["uri"],
            "priority": priority,
            "preferenceScore": 0,
        }

        missing_required = [item["id"] for item in required if not capability_matches(item, capabilities)]
        if missing_required:
            evidence["outcome"] = "rejected-required"
            evidence["missingRequired"] = missing_required
            result["candidates"].append(evidence)
            evidence_by_uri[endpoint["uri"]] = evidence
            continue

        matched_excluded = [item["id"] for item in excluded if capability_matches(item, capabilities)]
        if matched_excluded:
            evidence["outcome"] = "rejected-excluded"
            evidence["matchedExcluded"] = matched_excluded
            result["candidates"].append(evidence)
            evidence_by_uri[endpoint["uri"]] = evidence
            continue

        matched_preferred = [item["id"] for item in preferred if capability_matches(item, capabilities)]
        score = sum(item["weight"] for item in preferred if capability_matches(item, capabilities))
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


def cmd_select(args: argparse.Namespace) -> int:
    resolution = load_json(args.resolution)
    request = load_json(args.request)
    evaluated = parse_time(args.at) if args.at else datetime.now(timezone.utc)
    selection = generate_selection(resolution, request, evaluated)
    write_json(selection, args.out)
    return 0 if selection["terminal"] == "selected" else 3


def cmd_explain(args: argparse.Namespace) -> int:
    selection = load_json(args.selection)
    print(f"Selection {selection.get('selectionId', '<unknown>')}")
    print(f"Target: {selection.get('target', '<unknown>')}")
    print(f"Terminal: {selection.get('terminal', '<unknown>')}")
    if selection.get("selectedEndpoint"):
        print(f"Selected endpoint: {selection['selectedEndpoint']}")
    print("Candidates:")
    for item in selection.get("candidates", []):
        details: list[str] = []
        if item.get("missingRequired"):
            details.append("missing=" + ",".join(item["missingRequired"]))
        if item.get("matchedExcluded"):
            details.append("excluded=" + ",".join(item["matchedExcluded"]))
        if item.get("matchedPreferred"):
            details.append("preferred=" + ",".join(item["matchedPreferred"]))
        suffix = ("; " + "; ".join(details)) if details else ""
        print(
            f"  - {item['uri']}: {item['outcome']} "
            f"(priority={item.get('priority', 0)}, score={item.get('preferenceScore', 0)}){suffix}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tilden", description="Reference CLI for the Tilden federation specs")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve", help="resolve an identifier from a deterministic reference directory")
    resolve.add_argument("identifier")
    resolve.add_argument("--directory", required=True, help="JSON reference directory")
    resolve.add_argument("-o", "--out")
    resolve.set_defaults(func=cmd_resolve)

    request = sub.add_parser("request", help="create a short-lived caller-side TildenRequest")
    request.add_argument("identifier")
    request.add_argument("--resolution", help="bind request to an exact resolution digest")
    request.add_argument("--require", action="append", default=[], metavar="CAP")
    request.add_argument("--prefer", action="append", default=[], metavar="CAP[@WEIGHT]")
    request.add_argument("--exclude", action="append", default=[], metavar="CAP")
    request.add_argument("--ttl", type=int, default=300, help="lifetime in seconds (default: 300)")
    request.add_argument("-o", "--out")
    request.set_defaults(func=cmd_request)

    select = sub.add_parser("select", help="select an endpoint and emit TildenSelection evidence")
    select.add_argument("resolution")
    select.add_argument("request")
    select.add_argument("--at", help="evaluation time as RFC 3339; defaults to now")
    select.add_argument("-o", "--out")
    select.set_defaults(func=cmd_select)

    explain = sub.add_parser("explain", help="render a TildenSelection evidence record for a human")
    explain.add_argument("selection")
    explain.set_defaults(func=cmd_explain)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if getattr(args, "ttl", 1) <= 0:
            raise ValueError("ttl must be positive")
        return args.func(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"tilden: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
