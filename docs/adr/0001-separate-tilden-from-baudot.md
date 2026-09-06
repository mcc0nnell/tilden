# ADR 0001: Keep Tilden independent from Baudot

Status: Accepted  
Date: 2026-09-05

## Context

Tilden defines addressing, identity resolution, capability discovery, authority, trust, and routing metadata for federated accessible calling. Baudot is an interoperability runtime concerned with establishing and validating accessible sessions across independently implemented communications systems.

Embedding Tilden inside Baudot would make the federation contract appear implementation-specific and could discourage independent resolvers, national networks, enterprise platforms, and other runtimes from adopting it.

## Decision

Tilden is a standalone project and protocol surface.

Baudot may depend on the Tilden contract and provide the first reference consumer. Tilden must not depend on Baudot runtime internals.

The normative boundary is:

> Tilden determines who/where/how an identity can be reached. Baudot determines whether the resulting systems can actually establish an interoperable accessible session.

## Consequences

- Tilden schemas and specifications remain usable by non-Baudot implementations.
- Baudot can reject a successfully resolved endpoint when runtime security, policy, or interoperability checks fail.
- Tilden discovery transports and trust profiles can evolve independently of Baudot signaling/media adapters.
- Conformance can distinguish resolution correctness from session interoperability.
- Cross-project integration requires a stable, versioned handoff object.
