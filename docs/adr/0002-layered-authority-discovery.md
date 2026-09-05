# ADR 0002: Use layered authority discovery

Status: Accepted for Draft 0.1

## Context

Tilden must resolve identities across telephone numbering systems, Internet-style identities, enterprise namespaces, and national accessibility networks. No single discovery transport cleanly covers all of those environments.

ENUM is relevant to E.164 numbers, WebFinger and HTTPS are natural for domain-scoped identities, and DNS service binding may be useful for infrastructure discovery. Choosing one of these as the universal Tilden transport would couple the federation model to a deployment assumption that may not hold worldwide.

## Decision

Tilden discovery is a deterministic chain of authenticated authority delegations.

The core protocol defines the output object. Discovery profiles define:

1. identifier normalization;
2. initial authority derivation;
3. permitted discovery mechanisms;
4. deterministic mechanism order;
5. trust requirements for every delegation hop;
6. freshness and fallback behavior.

Discovery transports are adapters to that authority model, not the authority model itself.

Baudot receives a validated `TildenResolution` and does not need to understand the raw discovery mechanisms.

## Consequences

- Tilden can support E.164 and Internet-native identities without pretending they have identical governance.
- Jurisdictions can integrate existing numbering and portability authorities without becoming global dependencies.
- Domain owners can participate using Internet-native mechanisms.
- A future transport can be added without changing the Baudot handoff object.
- Implementations must preserve an auditable authority chain and cannot simply race discovery transports.
- Trust failure cannot silently downgrade into an unauthenticated fallback.

## Rejected alternatives

### Make ENUM the universal Tilden registry

Rejected because ENUM is highly relevant to E.164 but is not a universal identity or governance system and public deployment assumptions vary.

### Make HTTPS well-known the universal registry

Rejected because telephone-number authority and number portability cannot safely be inferred from an arbitrary web domain.

### Let clients try every mechanism and accept the first success

Rejected because this makes authority ambiguous and creates downgrade and hijack paths.
