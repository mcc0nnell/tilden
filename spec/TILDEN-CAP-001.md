# TILDEN-CAP-001: Endpoint Capability Registry

Status: Draft

## 1. Purpose

Tilden resolution may consider endpoint capabilities when choosing among communications routes. This document defines the initial vocabulary and, more importantly, the privacy semantics of those capability tokens.

## 2. Core rule

A Tilden capability describes what a communications endpoint or path can support.

It MUST NOT be interpreted as a diagnosis, disability label, demographic claim, or personal identity attribute of the person associated with the number.

For example:

```text
asl
```

means:

> this route can support an ASL-capable communication path

It does not mean:

> this person is Deaf

## 3. Capability classes

### 3.1 Media

Initial media tokens:

- `audio` — real-time audio
- `video` — real-time video
- `text` — real-time or session-associated text

### 3.2 Transport

Initial protocol tokens:

- `sip` — SIP signaling endpoint
- `webrtc` — WebRTC-capable endpoint
- `rtt` — real-time text capability, including an applicable RTT interworking path
- `pstn` — conventional telephone-network interconnection path

Protocol tokens describe the route presented to the relying party. They do not require the ultimate session to remain on that protocol end-to-end.

### 3.3 Interaction and accessibility

Initial feature tokens:

- `asl` — supports an ASL-capable video communications path
- `captions` — supports caption delivery or caption-capable interworking
- `relay` — supports a relay-mediated communications path
- `direct-video` — supports direct video communication without requiring a voice-leg relay path
- `rtt-interworking` — supports RTT conversion or interworking where needed

These tokens are deliberately functional rather than identity-based.

### 3.4 Security

Initial security tokens:

- `e2ee` — the offered path supports an end-to-end encryption mode defined by the selected transport/profile
- `authenticated-endpoint` — the endpoint can present transport/profile-defined authentication
- `federation-authenticated` — the route was learned through an authenticated Tilden federation relationship

A token MUST NOT claim stronger security semantics than the underlying transport can actually provide.

## 4. Query semantics

A relying party MAY include capabilities in a resolution request to avoid receiving unusable routes.

Example:

```json
{
  "capabilities": {
    "media": ["video", "text"],
    "protocols": ["sip", "webrtc"],
    "features": ["asl"]
  }
}
```

A resolver SHOULD interpret capability queries as requirements of the attempted communication, not as permanent attributes of the caller.

## 5. Response semantics

An endpoint MAY advertise capabilities such as:

```json
{
  "uri": "sip:alice@example.net",
  "protocol": "sip",
  "capabilities": ["video", "asl", "rtt", "e2ee"]
}
```

The presence of a capability means the endpoint is eligible for that behavior under the current resolver policy. It does not guarantee that every session will successfully negotiate it.

## 6. Matching

The initial resolver profile uses these rules:

- requested protocols are alternatives unless a later profile says otherwise;
- requested media are alternatives unless explicitly marked required;
- requested features are requirements;
- resolver policy may impose additional constraints;
- a relying party may reject a returned endpoint if local negotiation cannot satisfy the actual session requirements.

Later revisions should replace these coarse rules with an explicit requirement/preference expression if needed.

## 7. Minimal disclosure

Resolvers SHOULD avoid publishing a complete capability inventory when a narrower answer is sufficient.

For example, a caller asking for an ASL-capable route can receive one compatible endpoint without learning whether the same number also has captioning, relay, PSTN, or other private routes.

## 8. Anti-inference rule

Implementations MUST NOT infer personal characteristics from endpoint capability metadata for unrelated purposes.

Capability information should not be repurposed for advertising, profiling, eligibility decisions, analytics about disability status, or other non-routing uses merely because it appears in a Tilden transaction.

## 9. Extensibility

Unknown capability tokens MUST be ignored unless the requesting profile marks them critical.

New standardized tokens should document:

- functional meaning;
- negotiation behavior;
- privacy impact;
- downgrade risk;
- relationship to existing communications standards.

Private experimental tokens SHOULD use a collision-resistant namespace convention defined by a future registry profile.

## 10. Open questions

- whether RTT is best represented only as media/feature rather than also a protocol token;
- how to express required versus preferred capabilities;
- how language preferences interact with ASL and spoken-language interpretation;
- how relay modality should be represented without revealing sensitive service enrollment;
- whether security capabilities belong in the same registry or a separate assurance registry;
- how capability tokens map to SDP, SIP feature tags, WebRTC negotiation, and Baudot adapters.
