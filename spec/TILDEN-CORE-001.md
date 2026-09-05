# TILDEN-CORE-001: Programmable Number Resolution

**Status:** Draft  
**Category:** Core Architecture  
**Version:** 0.1

## Abstract

Tilden defines a neutral resolution layer for real-time communications. A Tilden identifier names a persistent communications identity rather than a fixed carrier, device, application, trunk, or protocol endpoint.

A resolver accepts an identifier and relevant session capabilities, evaluates authoritative routing policy, and returns one or more compatible destinations. Media does not need to traverse the resolver.

> **A Tilden number is a persistent communications identity whose current network destination is resolved programmatically.**

This permits an E.164 telephone number to remain stable while the services capable of receiving communications for that number change over time.

## 1. Architectural principle

Traditional telephone numbering often binds a number, through several layers of routing infrastructure, to a provider or network termination. Tilden separates the durable identifier from those terminations.

```text
identifier
    |
    v
Tilden resolver
    |
    +--> identity / authority
    +--> endpoint discovery
    +--> capability matching
    +--> accessibility policy
    +--> routing policy
    |
    v
ordered destinations
    |
    +--> SIP / VRS
    +--> WebRTC
    +--> RTT
    +--> PSTN
    +--> native video calling
    +--> future transports
```

The resolver is a **control-plane component**. It does not need to terminate, relay, transcode, or otherwise carry the media session.

## 2. Goals

Tilden is intended to:

1. preserve a stable human-reachable communications identity while endpoints change;
2. support multiple providers, applications, devices, and transports behind one identifier;
3. make accessibility capabilities first-class routing inputs;
4. permit federated resolution without requiring a single global provider or calling stack;
5. interoperate with existing E.164, SIP, RTT, WebRTC, VRS, and PSTN infrastructure;
6. allow new transports and capabilities to be introduced without redesigning numbering;
7. provide a clean resolution interface for interoperability systems such as Baudot.

## 3. Non-goals

Tilden does not define:

- a media codec;
- a SIP implementation;
- a VRS provider;
- a media relay or TURN service;
- a transcoder;
- a universal identity provider;
- a requirement that media traverse the Tilden resolver;
- a requirement to use any particular edge or cloud vendor.

## 4. Identifier model

A Tilden deployment MAY accept multiple identifier forms. The initial numbering profile is expected to support E.164 telephone numbers.

Implementations MUST normalize identifiers before authoritative resolution. A deployment SHOULD retain the identifier type in its canonical representation so that future identifier families do not collide.

Example canonical identifiers:

```text
e164:+12025550142
sip:alice@example.net
```

The existence of an E.164 profile does not imply that Tilden owns or replaces the E.164 numbering system. Tilden resolves communications identities that an authority is permitted to publish.

## 5. Resolution function

Conceptually, a Tilden resolver implements the following function:

```text
resolve(identifier, session_context) -> resolution_object
```

`session_context` MAY contain information needed to select compatible routes, including:

- requested media modalities;
- caller transport capabilities;
- accessibility capabilities;
- authenticated caller or federation context;
- network or regulatory constraints;
- privacy-preserving policy signals.

A resolver MUST NOT require information that is unnecessary to make the routing decision.

## 6. Resolution object

A successful resolution returns an object containing the subject, authority information, cache lifetime, and one or more candidate endpoints.

Illustrative example:

```json
{
  "version": "tilden/0.1",
  "subject": "e164:+12025550142",
  "authority": "https://resolver.example",
  "ttl": 60,
  "endpoints": [
    {
      "id": "primary-video",
      "transport": "sip",
      "uri": "sip:alice@vrs.example",
      "priority": 10,
      "capabilities": ["video", "signed-language", "rtt", "e2ee"]
    },
    {
      "id": "browser",
      "transport": "webrtc",
      "uri": "https://call.example/alice",
      "priority": 20,
      "capabilities": ["video", "audio", "rtt"]
    },
    {
      "id": "fallback",
      "transport": "pstn",
      "uri": "tel:+12025550142",
      "priority": 100,
      "capabilities": ["audio"]
    }
  ]
}
```

The endpoint list is ordered by policy. A consumer MAY further filter the returned set according to capabilities it can actually satisfy.

Endpoint and capability registries are expected to evolve independently of the core resolution model.

## 7. Resolution flow

A typical call flow is:

```text
Incoming communication
        |
        v
PSTN / SIP / app / federation ingress
        |
        v
normalize destination identifier
        |
        v
Tilden resolution request
        |
        v
policy + capability evaluation
        |
        v
ordered endpoint set
        |
        v
transport / interoperability layer
        |
        v
selected destination
```

The Tilden transaction can finish before session establishment begins. After resolution, the caller or an interoperability component establishes the actual communication using the selected transport.

## 8. Relationship to Baudot

Tilden and Baudot have separate responsibilities.

**Tilden answers:** *Where and how should this communications identity be reached?*

**Baudot answers:** *How do the selected communications systems interoperate?*

A typical combined deployment is:

```text
number
  |
  v
Tilden
  |  ordered routes + capabilities
  v
Baudot
  |  protocol interop / gateway behavior
  v
SIP | VRS | WebRTC | RTT | native calling | PSTN
```

Baudot is expected to be an early reference consumer of Tilden resolution objects, but neither project requires the other to exist.

## 9. Edge-runtime profile

A Tilden resolver MAY be implemented as a lightweight edge function. For example, an HTTPS request for an E.164 identifier could be handled by a Cloudflare Worker or an equivalent serverless runtime.

An edge implementation can perform:

- authority validation;
- endpoint lookup;
- capability negotiation;
- accessibility preference evaluation;
- authorization checks;
- route ordering;
- short-lived caching.

Persistent per-identity or per-session state MAY be provided by a stateful edge primitive such as a durable object, database, or equivalent service.

The Tilden protocol MUST NOT depend on Cloudflare-specific APIs. Cloudflare Workers are an implementation profile, not the architecture.

## 10. Security and privacy

A Tilden implementation MUST treat resolution data as security-sensitive communications metadata.

At minimum:

1. authoritative resolution responses MUST be authenticated, either by the secure resolution channel, object signatures, or both;
2. an authority MUST demonstrate control over identifiers it publishes;
3. resolver implementations SHOULD minimize endpoint disclosure and enumeration risk;
4. presence information MUST NOT be exposed merely because a caller can resolve an identifier;
5. short-lived routes, opaque rendezvous URIs, or authenticated resolution SHOULD be available where static endpoint publication would create privacy or abuse risk;
6. caches MUST honor authority changes and bounded lifetimes;
7. consumers MUST treat endpoint URIs and capability metadata as untrusted input until authority validation succeeds.

Tilden resolution is not itself proof that the eventual media path is end-to-end encrypted. Encryption properties belong to the selected session transport and MUST be represented accurately.

## 11. Federation

Tilden is designed for federation. A deployment MAY delegate authoritative resolution for an identifier or identifier range to another resolver.

The bootstrap and delegation mechanism is intentionally left open in version 0.1. Candidate mechanisms include DNS-based discovery, well-known HTTPS metadata, numbering-database integration, and explicit federation configuration.

Whatever mechanism is selected MUST permit independent authorities to participate without requiring all Tilden identifiers to be hosted by one operator.

## 12. Open questions

The following remain deliberately unresolved:

- authoritative proof of control for E.164 numbers;
- federation bootstrap and delegation;
- resolver discovery;
- signed-object format;
- cache invalidation semantics;
- capability vocabulary and registry governance;
- privacy-preserving discovery for non-public endpoints;
- emergency calling and jurisdiction-sensitive routing;
- number portability interactions;
- abuse handling and revocation.

These questions should be resolved in separate, reviewable specification increments rather than embedded as vendor-specific assumptions in the core architecture.
