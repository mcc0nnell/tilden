# Tilden

**Federated identity, addressing, discovery, trust, capability selection, and routing evidence for accessible real-time communications.**

Tilden defines a neutral resolution layer for worldwide accessible calling. It maps human-reachable identifiers to authoritative federation endpoints and selects a route that satisfies one call's accessibility requirements without requiring the world to adopt a single provider, national platform, or calling stack.

## North star

A person should be able to reach another person across providers, platforms, modalities, languages, and national networks without bespoke bilateral integration between every system.

```text
identifier
  -> TILDEN-CORE-001
  -> TILDEN-DISCOVERY-001
  -> TILDEN-TRUST-001
  -> TILDEN-CAP-001
  -> TILDEN-REQUEST-001
  -> TILDEN-SELECTION-001
  -> selected endpoint + evidence
  -> calling runtime
```

## Tilden and Baudot

Tilden and Baudot are deliberately separate projects.

- **Tilden:** who, where, and how an accessible identity can be reached, which endpoint best satisfies a call's requirements, and why that route was chosen.
- **Baudot:** whether independently implemented systems can establish an interoperable accessible session over the selected route.

Baudot is expected to be the first reference consumer of Tilden selection output, but Tilden is intentionally usable without Baudot.

## Reference CLI

A stdlib-only reference CLI makes the current stack executable.

```bash
python -m pip install -e .

tilden resolve tel:+12025550123 \
  --directory conformance/reference/directory.json \
  -o /tmp/resolution.json

tilden request tel:+12025550123 \
  --resolution /tmp/resolution.json \
  --require 'video.sign:languages=ase' \
  --require text.rtt \
  --prefer security.e2ee@100 \
  -o /tmp/request.json

tilden select /tmp/resolution.json /tmp/request.json \
  -o /tmp/selection.json

tilden explain /tmp/selection.json
```

The reference directory is deterministic test data, not a claim that global Tilden discovery is already deployed. Network discovery transports remain governed by `TILDEN-DISCOVERY-001` and future profiles.

See [`docs/cli.md`](docs/cli.md) for command details.

## Specification stack

- [`TILDEN-CORE-001`](spec/TILDEN-CORE-001.md): canonical resolution contract.
- [`TILDEN-DISCOVERY-001`](spec/TILDEN-DISCOVERY-001.md): layered authority discovery.
- [`TILDEN-TRUST-001`](spec/TILDEN-TRUST-001.md): signed resolution and trust verification.
- [`TILDEN-CAP-001`](spec/TILDEN-CAP-001.md): accessible communication capability vocabulary.
- [`TILDEN-REQUEST-001`](spec/TILDEN-REQUEST-001.md): short-lived caller-side call requirements.
- [`TILDEN-SELECTION-001`](spec/TILDEN-SELECTION-001.md): deterministic endpoint selection and routing evidence.

Machine-readable objects live under [`schemas/`](schemas/), with executable conformance fixtures under [`conformance/`](conformance/).

## Repository layout

```text
src/tilden/    reference executable
spec/          normative specifications
schemas/       machine-readable protocol schemas
registry/      capability registry
examples/      canonical object examples
conformance/   executable interoperability/conformance fixtures and reference data
docs/          architecture, CLI guide, handoff notes, ADRs
tools/         validation and development utilities
```

## Design invariants

1. No mandatory single provider or global operator.
2. Tilden does not depend on Baudot runtime internals.
3. Telephone numbers remain first-class, but are not the only possible identity model.
4. Trust, authority, delegation, expiry, and downgrade behavior are explicit.
5. Accessibility capability disclosure is minimized because it can be privacy-sensitive.
6. Per-call requirements are ephemeral and caller-side by default.
7. Selection is deterministic and explainable.
8. Resolution or selection success is not session interoperability success.

## Status

Early protocol design and reference implementation. Draft profiles, transports, trust anchors, digest profiles, and wire formats may change before 1.0.

Licensed under Apache-2.0.
