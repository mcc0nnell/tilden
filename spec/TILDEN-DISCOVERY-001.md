# TILDEN-DISCOVERY-001: Federated Discovery

Status: **Draft 0.1**  
Specification ID: `TILDEN-DISCOVERY-001`  
Depends on: `TILDEN-CORE-001`

## 1. Purpose

This specification defines how a Tilden resolver discovers the authority and retrieval location needed to produce a `TildenResolution` object.

Discovery is deliberately separate from the core resolution object. Tilden MUST be able to evolve discovery transports without changing the object consumed by Baudot or another relying implementation.

## 2. Design rule

Discovery is a chain of authority, not a race among endpoints.

A resolver MUST NOT accept whichever transport answers first. Each discovery step must derive from the identifier or from an explicitly trusted delegation produced by the previous step.

```text
input identifier
      |
      v
canonicalize
      |
      v
derive namespace authority
      |
      v
bootstrap discovery service
      |
      v
retrieve assertion
      |
      v
validate authority + trust + freshness
      |
      v
TildenResolution
```

## 3. Supported identifier profiles

Draft 0.1 defines two baseline discovery classes.

### 3.1 E.164 telephone identifiers

Input form:

```text
tel:+12025550123
```

Resolvers supporting the E.164 profile MUST normalize the input to a globally qualified E.164 number before discovery.

The authority bootstrap for an E.164 identity is profile-defined because number portability and authoritative routing data differ by jurisdiction. A profile MAY use:

- ENUM as defined by RFC 6116;
- a national numbering or portability authority service;
- a regulator-designated directory;
- another authenticated delegation mechanism.

A resolver MUST NOT assume that public ENUM coverage exists for every E.164 number.

The result of the E.164 bootstrap step MUST identify either an authoritative Tilden assertion endpoint or another authenticated delegation step.

### 3.2 Domain-scoped identities

Examples include:

```text
acct:alice@example.net
sip:alice@example.net
```

For a domain-scoped identifier, the domain is the initial namespace authority unless the identifier profile explicitly defines another authority derivation rule.

A profile MAY use WebFinger (RFC 7033), an HTTPS well-known resource, DNS service discovery, or another authenticated domain-controlled mechanism to locate a Tilden assertion endpoint.

Draft 0.1 does not reserve a WebFinger relation or IANA well-known URI. Implementations MUST treat any provisional identifier for such a resource as experimental until a stable registration strategy is adopted.

## 4. Discovery transports

Tilden discovery is transport-pluggable. The following transports are candidates, not universal requirements.

### 4.1 ENUM

ENUM maps E.164 telephone numbers through DNS to URI-oriented service data and is therefore a natural bootstrap mechanism for telephone-number identities.

Tilden implementations using ENUM MUST follow RFC 6116 processing rules and MUST define how an ENUM result delegates to a Tilden assertion endpoint.

Tilden MUST NOT redefine generic ENUM processing.

### 4.2 WebFinger

WebFinger can discover information associated with URI-identified people or entities over HTTPS.

A Tilden WebFinger profile MUST define a stable link relation identifying the Tilden assertion endpoint before it can be considered interoperable. Draft 0.1 leaves that relation open.

### 4.3 HTTPS well-known discovery

A domain profile MAY expose a Tilden bootstrap document over HTTPS. The final well-known URI name and media type are intentionally not frozen in Draft 0.1 pending registration and deployment evidence.

TLS server identity validation is mandatory for HTTPS discovery. Failure to authenticate the expected authority MUST produce `untrusted`, not transparent fallback.

### 4.4 DNS service binding

SVCB-style discovery as defined by RFC 9460 is attractive for locating alternate service endpoints and carrying connection parameters.

Tilden MUST NOT repurpose the HTTPS RR with semantics that conflict with RFC 9460. Any future Tilden-specific SVCB mapping must define the service mapping and registration requirements explicitly.

## 5. Resolution algorithm

A conforming resolver performs the following logical steps:

1. Parse the input identifier.
2. Normalize it according to its identifier profile.
3. Derive the initial namespace authority.
4. Select only discovery mechanisms permitted by the active profile.
5. Follow authenticated delegations in deterministic order.
6. Retrieve a Tilden assertion.
7. Validate syntax against the active Tilden schema.
8. Validate that the assertion authority is permitted to speak for the canonical identity.
9. Validate trust and freshness.
10. Return the `TildenResolution` or a typed failure.

A profile MUST define deterministic ordering when more than one discovery mechanism is permitted.

## 6. Authority continuity

Every delegation step MUST preserve an auditable authority chain.

For example:

```text
E.164 identity
  -> national numbering authority
  -> provider federation authority
  -> signed Tilden assertion
```

or:

```text
acct:alice@example.net
  -> example.net
  -> authenticated discovery service
  -> signed Tilden assertion
```

The final assertion MUST NOT be trusted merely because it was retrieved from a reachable endpoint. The resolver must verify that the endpoint is authorized by the discovery chain.

## 7. Secure fallback

Fallback is permitted for availability but MUST NOT create a downgrade path.

If an authenticated mechanism returns a definitive trust failure, a resolver MUST NOT silently retry an unauthenticated mechanism and return that result as equivalent.

Resolvers SHOULD distinguish:

- transport unavailable;
- authority not found;
- authenticated negative response;
- trust validation failure;
- stale delegation;
- malformed assertion.

## 8. Caching

Each discovery step MAY be cached only within the freshness constraints of the mechanism that produced it.

The effective expiry of a resolution MUST NOT exceed the earliest relevant expiry in its authority chain.

A resolver MUST NOT extend the lifetime of an assertion beyond either:

- the assertion's `expiresAt`; or
- an earlier expiry imposed by a discovery/delegation step.

## 9. Portability

Portability is a first-class discovery requirement.

For E.164 identities, a jurisdiction profile SHOULD obtain current authoritative routing from the applicable portability or numbering source rather than permanently deriving provider identity from the number itself.

For domain-scoped identities, moving the service endpoint behind the authoritative domain MUST NOT require changing the user-facing identifier.

Discovery profiles that permanently bind an identity to one service provider MUST document that limitation.

## 10. Privacy

Discovery mechanisms SHOULD minimize disclosure of user-specific accessibility capabilities before an authenticated relying party needs them.

Public DNS bootstrap records SHOULD identify federation infrastructure or delegation targets rather than publishing detailed disability- or modality-specific user attributes whenever feasible.

Resolvers SHOULD avoid query patterns that make bulk enumeration of accessible users easier than necessary.

## 11. Evidence and observability

A resolver SHOULD be able to emit a machine-readable discovery trace containing:

- input identifier;
- canonical identifier;
- discovery profile;
- each authority/delegation hop;
- mechanism used;
- freshness data;
- validation result;
- terminal success or typed failure.

A discovery trace is evidence, not part of the core `TildenResolution` consumed by Baudot. Keeping the trace separate prevents operational evidence from becoming required session state.

## 12. Baudot interaction

Baudot SHOULD receive the validated `TildenResolution`, not raw ENUM, DNS, WebFinger, or directory responses.

This keeps discovery policy inside Tilden and keeps Baudot focused on session establishment and interoperability.

```text
ENUM / DNS / HTTPS / WebFinger / directory
                |
                v
              Tilden
                |
        validated resolution
                |
                v
              Baudot
                |
      session negotiation
```

## 13. Conformance

A conforming discovery implementation MUST:

1. deterministically normalize supported identifiers;
2. derive authority according to the active profile;
3. follow only profile-permitted discovery mechanisms;
4. validate authority continuity at each delegation boundary;
5. preserve trust failures instead of silently downgrading;
6. enforce the earliest relevant expiry in the discovery chain;
7. emit a schema-valid `TildenResolution` on success;
8. distinguish discovery success from Baudot/session success.

## 14. References

- RFC 6116 — E.164 to URI Dynamic Delegation Discovery System (ENUM)
- RFC 7033 — WebFinger
- RFC 9460 — Service Binding and Parameter Specification via DNS (SVCB and HTTPS RRs)

## 15. Open questions

Draft 0.1 intentionally leaves these unresolved:

- the baseline international E.164 authority bootstrap model;
- the exact number-portability integration profile for each jurisdiction;
- whether ENUM is baseline, optional, or bridge-only in production profiles;
- the stable WebFinger relation for Tilden;
- the stable HTTPS well-known URI and media type;
- a Tilden-specific SVCB mapping, if one is warranted;
- the mandatory cryptographic assertion envelope;
- privacy-preserving authenticated discovery for user-specific capabilities.
