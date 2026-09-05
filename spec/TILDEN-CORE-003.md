# TILDEN-CORE-003: Resolution Protocol

Status: Draft

## 1. Purpose

This document defines the initial protocol contract used by a relying party to resolve a Tilden identifier after discovering an authoritative resolver.

TILDEN-CORE-001 defines the programmable-numbering model. TILDEN-CORE-002 defines authority, delegation, and resolver discovery. This document defines the request and response exchanged with the resolver itself.

## 2. Resolution model

A Tilden resolution transaction is intentionally simple:

```text
relying party
    |
    | resolve(identifier, context)
    v
authoritative resolver
    |
    | signed resolution object
    v
candidate communications endpoints
```

The resolver returns routing metadata. It does not need to proxy signaling or media.

## 3. HTTP profile

The initial interoperable profile uses HTTPS.

A resolver SHOULD expose:

```text
POST /tilden/v1/resolve
Content-Type: application/json
Accept: application/tilden+json, application/json
```

HTTPS is the default transport for the control plane. Other transports may be defined by later profiles.

## 4. Request

A request contains the target identifier and MAY contain enough context to support capability-aware routing without disclosing unnecessary caller information.

Example:

```json
{
  "version": "0.1",
  "identifier": "tel:+12025550142",
  "requestId": "01J7TILDENEXAMPLE00000001",
  "capabilities": {
    "media": ["video", "audio", "text"],
    "protocols": ["sip", "webrtc", "rtt"],
    "features": ["asl", "e2ee"]
  }
}
```

The `identifier` field is required.

The `requestId` field SHOULD be unique for the resolution attempt.

Capability information is advisory. A caller MUST NOT be required to disclose accessibility or disability information merely to obtain a basic route.

## 5. Response

A successful resolver response contains:

- the normalized identifier;
- an issuance and expiration time;
- one or more candidate endpoints;
- optional capability metadata;
- optional routing priority or preference information;
- authority-binding information;
- a cryptographic proof.

Example:

```json
{
  "version": "0.1",
  "identifier": "tel:+12025550142",
  "issuedAt": "2026-09-05T21:40:00Z",
  "expiresAt": "2026-09-05T21:45:00Z",
  "endpoints": [
    {
      "id": "primary-video",
      "uri": "sip:alice@example.net",
      "protocol": "sip",
      "priority": 10,
      "capabilities": ["video", "asl", "rtt"]
    },
    {
      "id": "browser",
      "uri": "https://call.example.net/alice",
      "protocol": "webrtc",
      "priority": 20,
      "capabilities": ["video", "text"]
    }
  ],
  "authority": {
    "delegationSequence": 17,
    "verificationMethod": "did:web:example.net#tilden-1"
  },
  "proof": {
    "type": "ExampleSignature2026",
    "verificationMethod": "did:web:example.net#tilden-1",
    "proofValue": "..."
  }
}
```

## 6. Endpoint selection

The resolver MAY return multiple endpoints.

The relying party MAY choose among compatible endpoints according to:

- resolver-provided priority;
- local policy;
- supported transport;
- requested media;
- accessibility requirements;
- privacy and security requirements;
- cost or jurisdictional constraints where permitted by policy.

Returning an endpoint does not require the relying party to use it.

## 7. Capability semantics

Capabilities describe what an endpoint can support, not facts about the person associated with the identifier.

For example:

```text
"asl"
```

means the endpoint can participate in an ASL-capable communications path. It does not assert that the person is Deaf, uses ASL, or has any particular disability.

This distinction is normative and important for privacy.

## 8. Minimal disclosure

A resolver SHOULD return only the information required to establish an appropriate communication path.

Resolvers MAY vary responses based on authenticated caller class, federation relationship, jurisdiction, or other policy context.

Public unauthenticated resolution SHOULD avoid disclosing sensitive endpoint inventory, presence, accessibility preferences, or personally identifying metadata when a less revealing response is sufficient.

## 9. Errors

The HTTPS profile uses conventional HTTP status codes plus a Tilden error object.

Example:

```json
{
  "version": "0.1",
  "error": "not-found",
  "message": "No routable Tilden record is available for this identifier."
}
```

Initial error codes:

- `invalid-request`
- `not-found`
- `not-authorized`
- `temporarily-unavailable`
- `unsupported-identifier`
- `unsupported-capability`
- `stale-authority`
- `resolver-misconfigured`

A resolver SHOULD NOT reveal whether a private identifier exists when policy requires non-enumerability.

## 10. Caching

Resolution responses MUST contain an explicit expiration time or equivalent bounded freshness value.

A relying party MUST NOT use a cached response after expiry unless a profile explicitly defines degraded-mode behavior.

Short-lived resolution objects are preferred when routing state changes frequently.

## 11. Replay and binding

A signed response MUST be bound to the requested identifier.

Profiles MAY additionally bind responses to a request identifier, audience, nonce, caller federation, or other context when stronger replay protection is required.

## 12. Control-plane boundary

A Tilden resolver MUST NOT require media to traverse the resolver.

A resolver MAY return a URI that causes a later signaling transaction to traverse the same infrastructure, but that is an endpoint or gateway role distinct from Tilden resolution.

The canonical flow remains:

```text
resolve first
connect second
```

## 13. Baudot integration

A Baudot implementation may submit its supported protocols and capabilities in the resolution request, receive one or more candidate routes, and then establish or bridge the session using the selected route.

This permits Tilden and Baudot to evolve independently while remaining naturally composable.

## 14. Example end-to-end flow

```text
1. Caller dials +1 202 555 0142
2. Gateway normalizes to tel:+12025550142
3. Gateway discovers the authoritative Tilden resolver
4. Gateway validates the current delegation
5. Gateway POSTs a resolution request
6. Resolver returns signed candidate endpoints
7. Gateway validates freshness and authority binding
8. Gateway selects a compatible endpoint
9. Baudot / SIP / WebRTC / RTT signaling begins
10. Media flows independently of the Tilden resolver
```

## 15. Open questions

Later revisions should define:

- canonical media types and capability registries;
- authentication between federation participants;
- privacy-preserving query mechanisms;
- standardized signatures and canonicalization;
- conditional and policy-aware responses;
- response encryption;
- emergency-services behavior;
- bulk or recursive resolution;
- rate limiting and anti-enumeration requirements.
