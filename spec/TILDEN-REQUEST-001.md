# TILDEN-REQUEST-001: Ephemeral Accessible Call Requirements

Status: **Draft 0.1**  
Specification ID: `TILDEN-REQUEST-001`

## 1. Purpose

A `TildenRequest` expresses what a caller needs or prefers for one call after the target has been resolved and before a runtime such as Baudot begins session negotiation.

The request is intentionally ephemeral. It lets a caller say, for example, that this call requires signed-language video and real-time text and prefers end-to-end encryption without publishing those preferences into a Tilden directory record.

A request is an input to endpoint selection. It is not an identity record, a session description, or proof that the selected endpoint will interoperate.

## 2. Core boundary

```text
caller intent
    |
    v
TildenRequest
    +
validated TildenResolution
    |
    v
capability selection
    |
    v
selected endpoint
    |
    v
Baudot / other runtime
    |
    v
actual session negotiation
```

Tilden answers which authoritative endpoint best satisfies the request. Baudot or another runtime still determines whether the exact SIP, WebRTC, RTT, media, and security negotiation succeeds.

## 3. Privacy model

Draft 0.1 defines `TildenRequest` only for `local-selection` scope.

A conforming implementation MUST NOT publish a `TildenRequest` into a public or broadly enumerable directory. It SHOULD keep the request on the caller side through endpoint selection.

The object intentionally contains no required caller identity field.

A later profile may define selective disclosure or authenticated wire transport. Such a profile must address linkability, replay, consent, and unnecessary disclosure of disability-, language-, or relay-related information.

## 4. Object shape

The normative machine-readable form is `schemas/tilden-request.schema.json`.

A request contains:

- `version`: request object version;
- `scope`: `local-selection` in Draft 0.1;
- `requestId`: opaque per-request identifier;
- `nonce`: fresh unpredictable value used to reduce accidental replay/reuse;
- `target`: binding to the canonical target identity and optionally the exact resolution digest;
- `required`: capabilities that every acceptable endpoint must satisfy;
- `preferred`: capabilities that improve ranking but are not mandatory;
- `excluded`: capabilities or service properties that make an endpoint unacceptable;
- `createdAt` and `expiresAt`: short-lived freshness bounds.

Example:

```json
{
  "version": "0.1",
  "scope": "local-selection",
  "requestId": "req-7mC1vN4X1q9zR2Lp",
  "nonce": "m6p7qQw5g8Y0bXhTj3s2ZA",
  "target": {
    "canonicalIdentity": "tel:+33123456789",
    "resolutionDigest": "sha256:example"
  },
  "required": [
    {"id": "video.sign", "parameters": {"languages": ["ase"]}},
    {"id": "text.rtt"}
  ],
  "preferred": [
    {"id": "security.e2ee", "weight": 100}
  ],
  "excluded": [],
  "createdAt": "2026-09-05T21:10:00Z",
  "expiresAt": "2026-09-05T21:15:00Z"
}
```

## 5. Target binding

A request MUST name the canonical identity for which it was created.

If `resolutionDigest` is present, the selector MUST reject use of the request with a different resolution object.

This prevents a request prepared for one target or one authoritative resolution from being silently reused against another.

The digest algorithm and canonical digest representation are not frozen by Draft 0.1. Profiles that use `resolutionDigest` MUST define both.

## 6. Required capabilities

Every entry in `required` is conjunctive: an endpoint is acceptable only when it satisfies all required entries.

A missing required capability is a hard selection failure for that endpoint.

Examples include:

- `video.sign` for signed-language video;
- `text.rtt` for conversational real-time text;
- `security.e2ee` when end-to-end encryption is a hard requirement rather than merely a preference.

Required capabilities SHOULD be limited to properties necessary for this call. Implementations SHOULD NOT automatically copy a user's complete accessibility profile into every request.

## 7. Preferred capabilities

A `preferred` entry has a weight from 1 through 100.

After filtering endpoints that fail required or excluded constraints, the selector sums the weights of preferred entries matched by each endpoint. Higher scores rank first.

A preferred capability that is absent MUST NOT make the endpoint invalid.

Preference weights are local caller policy. They do not create global meaning such as one accessibility modality being more important than another.

## 8. Excluded capabilities

`excluded` lets local policy reject an endpoint when a particular capability or service property is present.

This is useful for consent and privacy constraints, such as refusing a relay-mediated route when the caller explicitly requires a direct endpoint.

Exclusions SHOULD be used narrowly because capability presence often describes what an endpoint can do, not what it will necessarily do for the call.

## 9. Parameter matching

Capability IDs use `TILDEN-CAP-001` semantics.

For Draft 0.1, parameter matching is deterministic and conservative:

1. if the request entry has no `parameters`, matching the capability ID is sufficient;
2. if a requested scalar parameter is present, the endpoint assertion must contain the same value;
3. if a requested array parameter is present, the endpoint assertion must contain at least one equal member;
4. if the endpoint omits a parameter constrained by the request, that entry does not match;
5. object-valued parameter matching requires a capability-specific profile and otherwise does not match.

Capability-specific specifications may define stricter semantics. They MUST NOT silently weaken a required constraint.

For example, a required `video.sign` with `languages: ["ase"]` matches an endpoint asserting `languages: ["ase", "bfi"]`, but not an endpoint asserting only `languages: ["fsl"]`.

## 10. Selection algorithm

Given one validated `TildenResolution` and one valid `TildenRequest`, a conforming selector MUST:

1. verify target identity binding;
2. verify `resolutionDigest` when present and supported by the active profile;
3. reject an expired or not-yet-valid request;
4. evaluate endpoint-level capabilities for each candidate endpoint;
5. remove endpoints missing any required entry;
6. remove endpoints matching any excluded entry;
7. score remaining endpoints by the sum of matched preferred weights;
8. rank higher preference score first;
9. use Tilden endpoint priority and deterministic URI ordering to break ties;
10. return either the selected endpoint plus selection evidence or a typed failure.

Identity-level capabilities MUST NOT be promoted into endpoint-level support when the chosen endpoint says otherwise.

## 11. Freshness and replay resistance

Requests are short-lived by design.

Implementations SHOULD use a lifetime of minutes, not hours or days, for interactive calling. A default operational profile should normally keep request lifetime at or below five minutes unless a use case requires otherwise.

`requestId` MUST be unique enough to distinguish concurrent calls. `nonce` SHOULD contain at least 128 bits of unpredictability when generated cryptographically.

A request MUST NOT be reused after `expiresAt`.

Draft 0.1 does not define a network replay cache because the object is local-selection-only. A future wire profile must do so.

## 12. Selection evidence

A selector SHOULD retain enough evidence to explain why an endpoint was selected or rejected without retaining unnecessary private preference data.

At minimum, evidence may record:

- request identifier;
- target canonical identity;
- candidate endpoint URI;
- missing required capability IDs;
- matched exclusion capability IDs;
- preferred score;
- selected endpoint URI;
- terminal selection result.

Evidence exported to WindAnvil or another assurance system SHOULD minimize language or disability-related details unless required for the test purpose.

## 13. Failure semantics

A selector SHOULD distinguish at least:

- `target_mismatch`;
- `resolution_mismatch`;
- `expired_request`;
- `no_capable_endpoint`;
- `excluded_by_policy`;
- `invalid_request`.

These are selection failures, not signaling failures.

## 14. Baudot handoff

Baudot SHOULD receive the selected endpoint, validated `TildenResolution`, and only the request constraints needed for runtime policy or negotiation.

Baudot MUST NOT infer that Tilden capability selection guarantees session success.

The complete private `TildenRequest` SHOULD remain caller-side unless a later profile explicitly authorizes disclosure.

## 15. Conformance

A conforming producer MUST:

1. emit a schema-valid request;
2. bind it to one canonical target identity;
3. generate a fresh request identifier and nonce;
4. set a finite expiration time;
5. avoid including caller identity unless required by a later profile.

A conforming selector MUST:

1. enforce target and freshness binding;
2. apply required, preferred, and excluded semantics deterministically;
3. use endpoint-level capability data for endpoint selection;
4. produce a deterministic result for equal inputs and policy;
5. distinguish selection failure from runtime negotiation failure.

Executable fixtures belong under `conformance/request/`.

## 16. Open questions

Draft 0.1 deliberately leaves open:

- signed or authenticated request envelopes;
- selective disclosure to a remote endpoint;
- privacy-preserving capability negotiation across federation boundaries;
- standardized digest binding to `TildenResolution`;
- whether caller language preferences need a dedicated profile beyond capability parameters;
- emergency-call request semantics;
- whether group calls require a multi-target request model;
- whether recurring or scheduled calls need a different lifetime profile.
