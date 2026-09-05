# Tilden reference CLI

The reference CLI executes the current Tilden stack locally. It is intentionally small and deterministic: it demonstrates the contracts without pretending that a global production discovery network already exists.

## Install

```bash
python -m pip install -e .
```

This installs the `tilden` command.

## `tilden resolve`

Resolve a canonical identifier from a deterministic reference directory:

```bash
tilden resolve tel:+12025550123 \
  --directory examples/reference-directory.json \
  -o resolution.json
```

The directory adapter is test infrastructure. It does not replace the discovery transports and authority rules defined by `TILDEN-DISCOVERY-001`.

## `tilden request`

Create a short-lived caller-side `TildenRequest`:

```bash
tilden request tel:+12025550123 \
  --resolution resolution.json \
  --require 'video.sign:languages=ase' \
  --require text.rtt \
  --prefer security.e2ee@100 \
  --ttl 300 \
  -o request.json
```

Capability shorthand is:

```text
capability.id
capability.id:key=value
capability.id:key=value1,value2;other=value
preferred.capability@WEIGHT
```

Examples:

```text
video.sign:languages=ase
text.rtt
security.e2ee@100
relay.interpreter
```

When `--resolution` is supplied, the generated request is bound to the deterministic digest of that exact resolution object.

`requestId` and `nonce` are freshly generated. The request expires after `--ttl` seconds, defaulting to 300 seconds.

## `tilden select`

Evaluate a resolution against one ephemeral request and produce `TildenSelection` evidence:

```bash
tilden select resolution.json request.json -o selection.json
```

Selection applies the Draft 0.1 semantics:

1. target and optional resolution-digest binding;
2. request freshness;
3. required-capability filtering;
4. excluded-capability filtering;
5. preferred-capability scoring;
6. endpoint priority;
7. deterministic URI tie-breaking.

A successful record contains `selectedEndpoint`. Rejections retain enough evidence to explain why each candidate failed.

For reproducible tests, `--at` can supply an RFC 3339 evaluation time instead of the current clock.

## `tilden explain`

Render selection evidence for a human:

```bash
tilden explain selection.json
```

Example shape:

```text
Selection sel-...
Target: tel:+12025550123
Terminal: selected
Selected endpoint: sip:secure@example-access.net
Candidates:
  - sip:plain@example-access.net: eligible (priority=1, score=0)
  - sip:secure@example-access.net: selected (priority=10, score=100); preferred=security.e2ee
```

## End-to-end demo

```bash
python -m pip install -e .

tilden resolve tel:+12025550123 \
  --directory examples/reference-directory.json \
  -o /tmp/tilden-resolution.json

tilden request tel:+12025550123 \
  --resolution /tmp/tilden-resolution.json \
  --require 'video.sign:languages=ase' \
  --require text.rtt \
  --prefer security.e2ee@100 \
  -o /tmp/tilden-request.json

tilden select /tmp/tilden-resolution.json /tmp/tilden-request.json \
  -o /tmp/tilden-selection.json

tilden explain /tmp/tilden-selection.json
```

The same flow runs in CI through `tools/test_reference_cli.py`.

## Digest warning

The reference CLI currently uses deterministic sorted-key JSON plus SHA-256 for local digest binding. That encoding is an implementation detail of the reference executable, **not yet the normative Tilden digest/canonicalization profile**. `TILDEN-SELECTION-001` deliberately leaves the final digest profile open.

## Baudot boundary

The useful handoff is the selected endpoint and `selectionId`, correlated with the validated resolution context. Baudot remains responsible for actual SIP/WebRTC/RTT/media/security negotiation and session-level interoperability evidence.
