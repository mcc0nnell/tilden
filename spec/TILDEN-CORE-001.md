# TILDEN-CORE-001: Federated Accessible Calling Resolution

Status: **Draft 0.1**  
Specification ID: `TILDEN-CORE-001`

## 1. Purpose

Tilden defines an implementation-neutral resolution contract for federated accessible real-time communications. It maps a human-reachable identifier to one or more authoritative federation endpoints, the capabilities exposed at those endpoints, trust material needed to evaluate the result, and expiry/freshness information.

Tilden does **not** define the call signaling or media runtime. A consumer such as Baudot may use a Tilden resolution to establish and negotiate a session.

## 2. Design goals

Tilden is designed to support:

- federation across independently operated accessibility providers and national networks;
- provider portability without forcing users to adopt a single global platform;
- multiple identifier forms, including E.164 telephone numbers and URI-style identities;
- capability discovery for accessible communications modalities;
- explicit authority, trust, freshness, and fallback semantics;
- machine-readable conformance testing;
- compatibility with legacy telephony while permitting non-PSTN identity models.

## 3. Non-goals

Tilden does not standardize:

- SIP, WebRTC, RTP, RTT, or other session/media protocols themselves;
- interpretation or relay service policy;
- national numbering allocation policy;
- billing, reimbursement, or regulatory eligibility;
- a mandatory central registry operator;
- a mandatory Tilden implementation language or runtime.

## 4. Resolution model

A Tilden resolver accepts an input identifier and returns a `TildenResolution` object.

```text
identifier
   |
   v
Tilden resolver
   |
   v
TildenResolution
   |- canonicalIdentity
   |- authority
   |- endpoints[]
   |- capabilities[]
   |- trust
   `- expiresAt
```

A successful resolution MUST identify the canonical identity being resolved and MUST provide sufficient authority and freshness information for a relying party to determine whether the result is acceptable.

## 5. Identifier forms

A Tilden implementation MAY support one or more identifier schemes. Initial interoperable profiles should include:

- `tel:` identifiers representing E.164 telephone numbers;
- URI-style federated identities, such as `acct:` or another explicitly profiled URI form;
- implementation-defined enterprise or national identifiers, provided their scheme and authority semantics are unambiguous.

Resolvers MUST NOT silently reinterpret one identifier scheme as another. Normalization rules MUST be deterministic and documented.

## 6. Resolution object

The normative machine-readable form is defined by `schemas/tilden-resolution.schema.json`.

At minimum, a resolution contains:

- `version`: Tilden object version;
- `canonicalIdentity`: normalized identity represented by the result;
- `authority`: entity or namespace authority responsible for the assertion;
- `endpoints`: one or more reachable federation endpoints;
- `capabilities`: identity-level or service-level accessibility capabilities;
- `trust`: integrity/authenticity metadata or a reference to the trust mechanism used;
- `expiresAt`: time after which the result MUST be treated as stale unless refreshed.

## 7. Endpoints

Each endpoint contains a URI plus optional priority, weight, transport hints, capabilities, and security properties.

Endpoint ordering MUST be deterministic when priorities are equal. Consumers MAY apply local policy when multiple equally valid endpoints exist, but MUST NOT invent capabilities that were not asserted.

## 8. Capability vocabulary

Tilden capability identifiers are extensible strings. The initial registry is intentionally small:

- `video.sign` — bidirectional video suitable for signed-language communication;
- `text.rtt` — real-time text semantics;
- `text.caption` — caption delivery;
- `audio.voice` — bidirectional voice audio;
- `relay.interpreter` — interpreted relay capability;
- `security.e2ee` — endpoint advertises an end-to-end encrypted session profile;
- `transfer.accessible` — accessible session transfer supported.

A capability assertion means the endpoint claims support; it does not prove interoperability. Conformance and runtime negotiation remain separate concerns.

Capability parameters MAY carry language, codec, media-profile, or implementation-specific values. Parameters MUST NOT redefine the meaning of the capability identifier itself.

## 9. Authority and trust

A Tilden resolution MUST identify the authority that made or delegated the routing assertion.

The core model does not mandate one global trust system. Profiles MAY use DNSSEC, PKI, signed JSON objects, national numbering authority data, enterprise identity systems, or other mechanisms, provided that:

1. the asserting authority is identifiable;
2. integrity/authenticity verification is defined;
3. expiry or revocation behavior is defined;
4. delegation is explicit where applicable;
5. downgrade to an unauthenticated result is not silent.

## 10. Freshness, caching, and portability

A resolution MUST include `expiresAt`. A resolver or consumer MAY cache a result until that time.

A stale result MUST NOT be treated as current solely because a prior call succeeded.

Provider portability is a core requirement: changing the authoritative route for an identity MUST NOT inherently require changing the identity itself. Profiles that bind identity permanently to a provider conflict with this goal and should document the limitation.

## 11. Privacy

Capability metadata can reveal disability- or communication-related information. Implementations SHOULD minimize capability disclosure to what is needed for successful federation and SHOULD avoid publishing unnecessary user-specific accessibility data.

Resolvers and directories SHOULD support designs where broad public enumeration of user identities is impractical.

## 12. Failure semantics

Resolvers SHOULD distinguish at least:

- `not_found` — no authoritative record exists;
- `temporarily_unavailable` — authoritative resolution cannot currently be completed;
- `untrusted` — a record was found but failed trust validation;
- `expired` — a record exists but is no longer fresh;
- `unsupported_identifier` — the resolver does not support the identifier scheme.

Consumers MUST NOT convert `untrusted` into `not_found` in security-sensitive diagnostics or evidence records.

## 13. Baudot handoff contract

Baudot is a reference consumer, not a required Tilden component.

The handoff boundary is:

```text
Tilden: who/where/how can this identity be reached?
Baudot: can these independently implemented systems establish an interoperable accessible session?
```

Baudot MAY consume `TildenResolution` objects directly. Baudot MUST remain able to reject an endpoint when session negotiation, conformance policy, or local security policy fails even if Tilden resolution succeeded.

Tilden MUST NOT depend on Baudot-specific runtime state.

## 14. Conformance

A conforming Tilden resolver MUST:

1. deterministically normalize supported identifiers;
2. emit schema-valid resolution objects;
3. expose authority and expiry information;
4. preserve trust failures as distinct failures;
5. avoid silently changing identifier schemes;
6. produce deterministic endpoint ordering for equal input and authority state.

A conforming consumer MUST:

1. reject schema-invalid results;
2. enforce expiry;
3. evaluate trust according to the active profile;
4. distinguish discovery success from session interoperability success.

Executable fixtures belong under `conformance/`.

## 15. Versioning

This draft uses object version `0.1`. Pre-1.0 versions may change incompatibly. Once a 1.0 core object is published, incompatible changes require a new major version.

## 16. Open questions

The following are deliberately not frozen in Draft 0.1:

- canonical URI scheme for provider-independent identities;
- mandatory baseline trust profile;
- whether capability registries are centralized, federated, or both;
- discovery transports (DNS, HTTPS well-known resources, ENUM-family mechanisms, directory APIs, or combinations);
- cryptographic envelope format;
- emergency-service routing semantics;
- international number-portability authority mapping.
