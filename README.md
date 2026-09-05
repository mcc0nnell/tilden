# Tilden

**Federated identity, addressing, discovery, and capability resolution for accessible real-time communications.**

Tilden defines a neutral resolution layer for worldwide accessible calling. It maps human-reachable identifiers to authoritative federation endpoints and capability metadata without requiring the world to adopt a single provider, national platform, or calling stack.

## North star

A person should be able to reach another person across providers, platforms, modalities, languages, and national networks without requiring bespoke bilateral integration between every system.

Tilden supplies the discovery contract:

```text
identifier
  -> normalization
  -> authority/delegation
  -> endpoint discovery
  -> accessibility capabilities
  -> trust + freshness
  -> TildenResolution
  -> calling runtime
```

## Tilden and Baudot

Tilden and Baudot are deliberately separate projects.

- **Tilden:** who, where, and how an accessible identity can be reached.
- **Baudot:** whether independently implemented systems can establish an interoperable accessible session.

Baudot is expected to be the first reference consumer of Tilden resolution objects, but Tilden is intentionally independent of Baudot.

## Draft specification

The first protocol surface is [`TILDEN-CORE-001`](spec/TILDEN-CORE-001.md), currently Draft 0.1.

It defines:

- identifier normalization;
- authoritative resolution;
- endpoint discovery;
- accessibility capability advertisement;
- trust and delegation metadata;
- expiry and caching semantics;
- provider portability expectations;
- privacy constraints;
- failure semantics;
- the versioned handoff contract used by consumers such as Baudot.

The machine-readable resolution object is defined in [`schemas/tilden-resolution.schema.json`](schemas/tilden-resolution.schema.json).

## Repository layout

```text
spec/          normative specifications
schemas/       machine-readable protocol schemas
examples/      example resolution objects
conformance/   executable interoperability/conformance fixtures
docs/          architecture and ADRs
tools/         validation and development utilities
```

## Design invariants

1. No mandatory single provider or global operator.
2. Tilden does not depend on Baudot runtime internals.
3. Telephone numbers remain first-class, but are not the only possible identity model.
4. Trust, authority, delegation, expiry, and downgrade behavior are explicit.
5. Accessibility capability disclosure is minimized because it can be privacy-sensitive.
6. Resolution success is not the same thing as session interoperability success.

## Status

Early protocol design. Names, transports, trust profiles, and wire formats may change before 1.0.

Licensed under Apache-2.0.
