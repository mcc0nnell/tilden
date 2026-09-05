#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tilden.cli import main

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "tel:+12025550123"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run() -> int:
    with tempfile.TemporaryDirectory() as tempdir:
        temp = Path(tempdir)
        resolution = temp / "resolution.json"
        request = temp / "request.json"
        selection = temp / "selection.json"

        assert main([
            "resolve", IDENTIFIER,
            "--directory", str(ROOT / "examples" / "reference-directory.json"),
            "-o", str(resolution),
        ]) == 0

        assert main([
            "request", IDENTIFIER,
            "--resolution", str(resolution),
            "--require", "video.sign:languages=ase",
            "--require", "text.rtt",
            "--prefer", "security.e2ee@100",
            "-o", str(request),
        ]) == 0

        assert main([
            "select", str(resolution), str(request),
            "-o", str(selection),
        ]) == 0

        record = load(selection)
        assert record["terminal"] == "selected"
        assert record["selectedEndpoint"] == "sip:secure@example-access.net"
        assert len(record["candidates"]) == 2
        assert record["candidates"][0]["uri"] == "sip:plain@example-access.net"
        assert record["candidates"][0]["outcome"] == "eligible"
        assert record["candidates"][1]["uri"] == "sip:secure@example-access.net"
        assert record["candidates"][1]["outcome"] == "selected"
        assert record["candidates"][1]["preferenceScore"] == 100

        assert main(["explain", str(selection)]) == 0

    print("PASS reference CLI end-to-end flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
