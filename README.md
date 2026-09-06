# Tilden

**Federated identity, addressing, discovery, and capability resolution for accessible real-time communications.**

Tilden defines a neutral resolution layer for accessible calling. It maps human-reachable identifiers to authoritative federation endpoints and capability metadata without requiring the world to adopt a single provider or calling stack.

Baudot is expected to be the first reference consumer of Tilden resolution objects, but Tilden is intentionally independent of Baudot.

## Core contract

The first protocol surface is [`TILDEN-CORE-001`](spec/TILDEN-CORE-001.md), currently Draft 0.1. Its machine-readable object is [`schemas/tilden-resolution.schema.json`](schemas/tilden-resolution.schema.json).

At the boundary:

```text
Tilden: who / where / how can this identity be reached?
Baudot: can the resolved systems establish an interoperable accessible session?
```

A successful resolution is not proof of call, media, accessibility, or security interoperability.

## Resolution shape

```text
human-reachable identifier
        |
        v
   Tilden resolver
        |
        v
  TildenResolution
        |
        +-- canonical identity
        +-- asserting authority
        +-- endpoints
        +-- accessibility capabilities
        +-- trust metadata
        `-- expiry
```

The core deliberately does not freeze one discovery transport. DNS/ENUM-family resolution, HTTPS resources, directory APIs, enterprise systems, and national-network profiles can be evaluated without baking one deployment model into the base object.

## Conformance

Install the development dependency and validate the examples/fixtures:

```bash
python -m pip install -e '.[dev]'
python tools/validate_examples.py
```

Current fixtures cover minimal and multimodal resolution objects. They validate the object boundary; they do not assert runtime call interoperability.

CI runs the same validation on pushes and pull requests.

## Research donors

Legacy and production-derived systems can supply scenarios without becoming normative dependencies. The first preserved donor is the public ACE Direct iTRS resolution flow:

- [`docs/provenance/ace-direct-itrs-resolution.md`](docs/provenance/ace-direct-itrs-resolution.md) records the pinned source surfaces and separates useful resolution concepts from implementation quirks.
- [`research/ace-itrs/`](research/ace-itrs/) contains deterministic offline mocks for direct discovery, aliasing, missing records, NAPTR/SRV routing, and bounded failure states.

These mocks never query production iTRS infrastructure and make no claim about current provider routing.

## Status

Tilden is pre-1.0 specification work. Open questions intentionally remain around discovery transports, mandatory trust profiles, cryptographic envelopes, emergency routing, and international portability authority models. Those should be closed with implementation and interoperability evidence rather than guessed into the core.

## Project name

The project name honors Edward Tilden, connecting modern federated addressing work to the long history of telecommunications numbering and public infrastructure.
