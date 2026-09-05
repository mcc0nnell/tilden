# ADR-0002: Authority follows the identifier, not the resolver

Status: Proposed

## Context

Tilden allows a persistent communications identifier to resolve through infrastructure that may change over time. A resolver might be hosted by a carrier, VRS provider, application vendor, Cloudflare Worker, enterprise, or individual.

If resolver possession were treated as proof of identifier authority, moving providers would create an ownership ambiguity and a compromised or abandoned resolver could retain control indefinitely.

## Decision

Tilden treats resolver hosting and identifier authority as separate concerns.

The authoritative party for an identifier may delegate resolution to a resolver operator. That delegation is explicit, bounded, verifiable, and replaceable.

A resolver is authoritative only while a valid authority chain delegates the identifier to it.

Therefore:

- hosting a resolver does not confer ownership or durable authority over an identifier;
- appearing as a communications endpoint does not confer authority over the identifier;
- changing resolver operators does not change the Tilden identity;
- portability is represented as a change in delegation;
- old delegations must be able to expire, be superseded, or be revoked;
- implementations should reject rollback to a previously superseded delegation.

## Consequences

### Positive

- numbers remain stable while providers and infrastructure change;
- edge and serverless implementations remain interchangeable;
- Tilden can integrate with existing numbering and portability systems instead of replacing them;
- resolver compromise can be contained without reassigning the underlying identifier;
- federation does not require a single Tilden hosting provider.

### Costs

- implementations need an authority bootstrap mechanism for each identifier namespace;
- key lifecycle, revocation, caching, and rollback protection become protocol concerns;
- E.164 integration requires careful alignment with existing numbering and portability authority.

## Non-decision

This ADR does not select the final public bootstrap mechanism for E.164 identifiers. DNS, HTTPS, numbering-administration data, portability-system integration, or a hybrid may be defined by a later profile.

## Principle

> The number owns the route. The route does not own the number.
