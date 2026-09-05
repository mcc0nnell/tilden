# TILDEN-CORE-002: Authority, Delegation, and Resolver Discovery

Status: Draft

## 1. Purpose

Tilden separates a persistent communications identifier from the provider, application, transport, or device currently serving it. That separation requires a portable way to answer two questions:

1. Who is authorized to publish resolution information for this identifier?
2. How does a caller discover the authoritative Tilden resolver for it?

This document defines the initial authority and delegation model for Tilden identifiers, including E.164 numbers.

## 2. Design goals

The authority model MUST:

- preserve continuity when an identifier changes providers or applications;
- avoid making any single Tilden implementation or hosting vendor the universal root of trust;
- allow an authoritative party to delegate resolution without surrendering control of the identifier;
- permit cryptographic verification of published routing metadata;
- support bounded caching and explicit revocation;
- make authority changes observable and auditable;
- keep media transport outside the numbering and resolution control plane.

## 3. Roles

Tilden distinguishes four roles.

### 3.1 Identifier authority

The identifier authority is the entity recognized as having the right to control resolution for a particular identifier.

For an E.164 number, the mechanism establishing that right may ultimately derive from existing numbering assignment, service-provider, portability, or administrative systems. Tilden does not redefine the legal allocation of telephone numbers.

### 3.2 Resolver operator

A resolver operator hosts one or more Tilden resolution endpoints.

The resolver operator MAY be the identifier authority, but need not be. An authority may delegate resolution to another operator while retaining the ability to replace or revoke that delegation.

### 3.3 Endpoint operator

An endpoint operator provides a reachable communications service such as SIP, VRS, WebRTC, RTT, PSTN interconnection, or another supported transport.

Endpoint operators do not acquire authority over the identifier merely because they appear in a resolution object.

### 3.4 Relying party

A relying party is a caller, gateway, communications application, Baudot node, or other system that resolves a Tilden identifier and relies on the result.

## 4. Authority chain

A relying party SHOULD be able to validate a bounded chain:

```text
identifier
    |
    v
recognized authority proof
    |
    v
delegation record
    |
    v
authoritative Tilden resolver
    |
    v
signed resolution object
    |
    v
communications endpoint(s)
```

The authority chain establishes control of the routing metadata. It does not authenticate the human identity of a caller or callee unless another protocol explicitly provides that property.

## 5. Delegation record

An authority MAY delegate resolution using a signed delegation record.

A delegation record SHOULD contain at least:

- the normalized identifier;
- the authoritative resolver URI;
- a public-key identifier or verification method;
- issuance time;
- expiration time or maximum validity interval;
- an optional sequence or version number;
- an optional previous-delegation reference;
- an optional revocation location;
- the authority's signature.

Example:

```json
{
  "identifier": "tel:+12025550142",
  "resolver": "https://resolver.example.net/tilden/v1/resolve",
  "verificationMethod": "did:web:example.net#tilden-1",
  "issuedAt": "2026-09-05T21:30:00Z",
  "expiresAt": "2026-10-05T21:30:00Z",
  "sequence": 17,
  "signature": "..."
}
```

The specific signature suite and proof format are registry items and are not fixed by this draft.

## 6. Resolver discovery

Tilden resolver discovery is intentionally separable from Tilden resolution.

A relying party first discovers which resolver is authoritative, then requests a current resolution object from that resolver.

### 6.1 Discovery mechanisms

A Tilden profile MAY define one or more discovery mechanisms, including:

- a registry or numbering-administration lookup;
- DNS-based delegation;
- an HTTPS well-known resource;
- a signed directory or federation feed;
- a carrier or portability-system bridge;
- a locally configured trust anchor for closed deployments.

No single discovery mechanism is mandatory for every identifier namespace.

### 6.2 E.164 profile

For E.164 identifiers, Tilden SHOULD integrate with existing numbering and portability authority rather than create a parallel allocation system.

The E.164 profile therefore separates:

```text
number allocation / portability authority
                |
                v
        Tilden delegation
                |
                v
        resolver operator
```

This allows the communications routing layer to change without changing who has legal or administrative control of the number.

## 7. Portability

Number portability is modeled as a change of authoritative delegation, not a change of Tilden identity.

When an identifier moves from provider A to provider B:

1. the identifier remains unchanged;
2. the prior delegation is revoked, expires, or is superseded;
3. a new delegation names the current authoritative resolver;
4. relying parties reject stale delegations after their validity interval;
5. endpoint routing changes independently of the identifier itself.

A Tilden implementation MUST NOT treat possession of an old endpoint or resolver record as perpetual proof of authority.

## 8. Caching and freshness

Resolvers and relying parties MAY cache delegation and resolution records.

Every cacheable authority record MUST have a bounded validity interval or equivalent freshness mechanism.

Clients SHOULD prefer the highest valid sequence or version they can authenticate and MUST NOT silently fall back to an older delegation after observing a newer valid one unless an explicit recovery policy permits it.

This rule is intended to reduce rollback attacks during provider changes or revocation.

## 9. Revocation

A Tilden authority model MUST support revocation of resolver delegation.

Revocation MAY be represented by:

- replacement with a higher-sequence delegation;
- an explicit revocation record;
- removal from the authoritative discovery source;
- short-lived delegations that expire naturally;
- another profile-defined mechanism with equivalent security properties.

Emergency revocation profiles SHOULD favor short propagation intervals over long cache lifetimes.

## 10. Resolver response binding

An authoritative resolver SHOULD cryptographically bind each returned resolution object to:

- the requested identifier;
- the resolver's current authority;
- an issuance time;
- an expiration time or TTL;
- an object version or nonce where replay protection requires it.

A relying party MUST NOT accept a validly signed resolution object for one identifier as authoritative for another.

## 11. Cloud edge profile

A Cloudflare Worker, Fastly Compute application, serverless function, conventional web service, or other edge runtime MAY act as a Tilden resolver operator.

The hosting platform is not itself the identifier authority unless the relevant authority chain explicitly says so.

For example:

```text
+1 202 555 0142
      |
      v
authority / portability system
      |
      v
signed Tilden delegation
      |
      v
https://tilden.example/resolve
      |
      v
Cloudflare Worker
      |
      v
signed resolution object
```

This keeps Tilden deployable on commodity edge infrastructure without coupling the protocol to any single vendor.

## 12. Security considerations

Implementations MUST consider at least:

- unauthorized delegation;
- stale-cache and rollback attacks;
- resolver compromise;
- key compromise and key rotation;
- enumeration of reachable identifiers;
- metadata leakage through capability discovery;
- downgrade attacks that suppress accessible communications modes;
- malicious redirection to fraudulent endpoints;
- denial of service against resolver or discovery infrastructure.

A Tilden resolver SHOULD disclose only the minimum metadata required for the requesting context.

## 13. Privacy considerations

Resolver discovery and resolution can reveal communication intent, user capabilities, provider relationships, or accessibility preferences.

Profiles SHOULD minimize public disclosure of sensitive capability information and SHOULD support authenticated or context-specific resolution responses where appropriate.

A publicly discoverable Tilden number does not imply that every endpoint, preference, or accessibility attribute associated with that number must be publicly enumerable.

## 14. Relationship to Baudot

Tilden authority establishes which routing information is authoritative.

Baudot may consume that routing information to establish or bridge a communications session, but Baudot does not become the numbering authority merely by completing the call.

In shorthand:

> Tilden proves who may answer where-and-how. Baudot performs the how.

## 15. Open questions

The following remain intentionally open for later profiles:

- the canonical E.164 authority bootstrap mechanism;
- integration with NPAC, carrier routing, and other national portability systems;
- whether DNS, HTTPS, or a hybrid becomes the default public discovery path;
- required signature suites;
- privacy-preserving capability queries;
- recovery after key loss;
- emergency calling behavior;
- enterprise and private-number namespaces;
- cross-country federation and numbering-policy boundaries.
