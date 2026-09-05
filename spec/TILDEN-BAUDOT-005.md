# TILDEN-BAUDOT-005: Baudot Discovery and Modality Binding

**Status:** Draft 0.1  
**Category:** Interoperability Profile  
**Updated:** 2026-09-05

## 1. Abstract

This specification defines how a Tilden Resolution Object advertises a Baudot-accessible communications service and how a Baudot implementation consumes that advertisement without collapsing identity, discovery, transport, and runtime readiness into one concept.

The central binding is:

```text
Tilden chooses the authorized service.
Baudot chooses and proves the usable transport.
```

A `baudot` capability in a verified Tilden Resolution Object identifies an HTTPS service resource. A client retrieves a short-lived Baudot Service Descriptor from that resource, selects a compatible transport, establishes the session using that transport's protocol, and applies Baudot modality-readiness semantics before declaring the session usable.

This profile is intentionally not a new media transport or a replacement for SIP, WebRTC, RTP, T.140, RFC 4103, RFC 8865, or the Relay User Equipment profile in RFC 9248.

## 2. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as normative requirements.

## 3. Design invariants

A conforming implementation MUST preserve all of the following distinctions:

```text
identity != network
origin != subject authority
signature != current authority
service discovery != transport readiness
signaling success != usable communication
```

The last two distinctions are the primary concern of this profile.

A successful Tilden lookup proves neither that a media session was established nor that an accessibility modality is usable.

A successful SIP dialog, WebRTC connection, REFER transaction, ICE state, or other signaling event likewise MUST NOT by itself be treated as proof of modality readiness.

## 4. Scope

This specification defines:

1. the meaning of a Tilden capability with `type: "baudot"`;
2. the Baudot Service Descriptor;
3. the relationship between signed Tilden capability metadata and dynamic Baudot service metadata;
4. transport selection across SIP and WebRTC reference profiles;
5. T.140 / RTT profile advertisement;
6. modality requirements and downgrade behavior;
7. handoff and transfer readiness rules;
8. failure and fallback behavior;
9. a machine-readable reference schema and validation vectors.

This specification does not define:

- a new media protocol;
- a proprietary Baudot signaling stack;
- WebRTC application signaling;
- SIP registration;
- VRS provider enrollment;
- relay-service authorization;
- caller authentication;
- user identity proofing;
- a replacement for RFC 9248;
- platform-native FaceTime or iMessage signaling.

## 5. Relationship to Tilden

TILDEN-CORE-001 defines the Resolution Object and the `baudot` capability type.

TILDEN-AUTH-003 determines which resolver may speak for a Tilden subject.

TILDEN-SIGN-004 allows the Resolution Object to remain independently verifiable after caching or federation.

This profile begins only after those checks have succeeded.

Reference flow:

```text
tel:+12025550123
        |
        v
AUTH-003 bootstrap
        |
        v
SIGN-004 verified Resolution Object
        |
        v
capability type = baudot
        |
        v
Baudot Service Descriptor
        |
        +------ SIP / RFC 4103
        |
        +------ WebRTC / RFC 8865
        |
        +------ optional RUE / RFC 9248 profile
        |
        v
runtime modality evidence
        |
        v
usable session
```

## 6. The `baudot` Tilden capability

A Baudot service is advertised using a normal Tilden capability record with:

```json
{
  "type": "baudot",
  "uri": "https://baudot.example.net/call/+12025550123",
  "priority": 10,
  "media": ["video", "audio", "rtt"],
  "features": ["asl", "direct", "t140"]
}
```

For this profile:

- `type` MUST equal `baudot`;
- `uri` MUST be an absolute HTTPS URI;
- `priority` participates in outer Tilden endpoint selection;
- `media` describes the maximum media classes the signed Tilden authority is willing to advertise through this Baudot service;
- `features` describes the maximum feature set the signed Tilden authority is willing to advertise through this Baudot service.

The `uri` identifies the Baudot service resource for the resolved subject. It is not itself a claim that any transport is currently usable.

## 7. Service resource

A client SHOULD retrieve the Baudot Service Descriptor with:

```http
GET /call/+12025550123 HTTP/1.1
Host: baudot.example.net
Accept: application/baudot+json
```

A successful response SHOULD use:

```text
Content-Type: application/baudot+json
```

The descriptor transport MUST use authenticated HTTPS.

The HTTPS origin MUST match the origin of the `baudot` capability URI unless another URI is explicitly authorized by a future profile.

A cross-origin redirect MUST NOT silently transfer the authority conveyed by the signed Tilden capability.

## 8. Baudot Service Descriptor

A descriptor describes the currently offered transport choices for exactly one Tilden subject and one Baudot service resource.

Example:

```json
{
  "baudot_version": "1",
  "subject": "tel:+12025550123",
  "service_uri": "https://baudot.example.net/call/+12025550123",
  "issued_at": "2026-09-05T21:00:00Z",
  "expires_at": "2026-09-05T21:05:00Z",
  "transports": [
    {
      "id": "sip-total-conversation",
      "type": "sip",
      "uri": "sips:+12025550123@sip.baudot.example.net;user=phone",
      "priority": 10,
      "media": ["video", "audio", "rtt"],
      "features": ["asl", "direct", "t140"],
      "profiles": ["t140-rfc4103"]
    },
    {
      "id": "webrtc-total-conversation",
      "type": "webrtc",
      "uri": "https://baudot.example.net/webrtc/+12025550123",
      "priority": 20,
      "media": ["video", "audio", "rtt"],
      "features": ["asl", "direct", "t140"],
      "profiles": ["t140-rfc8865"]
    }
  ],
  "readiness": {
    "contract": "baudot.modality-readiness@1",
    "required": {
      "rtt": ["rttNegotiated", "firstT140CharacterObserved"],
      "video": ["videoInbound", "videoDecoded", "videoRendered"]
    }
  }
}
```

## 9. Required descriptor fields

A descriptor MUST contain:

- `baudot_version` — descriptor version;
- `subject` — the exact Tilden subject represented by the service;
- `service_uri` — the exact Baudot capability URI from the parent Tilden Resolution Object;
- `issued_at` — descriptor issuance time;
- `expires_at` — descriptor expiration time;
- `transports` — zero or more currently advertised transport choices;
- `readiness` — the runtime evidence contract applicable to the advertised session.

A descriptor MAY contain extension fields.

Unknown fields MUST be ignored unless a future profile marks them critical.

## 10. Binding validation

Before using a descriptor, a client MUST validate all of the following:

1. the parent Tilden Resolution Object is currently acceptable under CORE-001, AUTH-003, and any required SIGN-004 policy;
2. the selected parent capability has `type: "baudot"`;
3. the descriptor was retrieved from the authorized service origin;
4. descriptor `subject` exactly equals the parent Tilden subject;
5. descriptor `service_uri` exactly equals the parent capability URI after URI normalization permitted by the implementation profile;
6. current time is not before `issued_at` beyond permitted clock skew;
7. current time is before `expires_at`;
8. each selected transport is compatible with caller requirements.

A descriptor that fails any required binding check MUST NOT be used to establish a Baudot session.

## 11. Capability narrowing

A dynamic service descriptor MUST NOT expand the effective capabilities authorized by the signed Tilden capability.

For media:

```text
effective_media = tilden.media INTERSECTION transport.media
```

For features:

```text
effective_features = tilden.features INTERSECTION transport.features
```

If the descriptor advertises additional media or features not present in the signed parent capability, those additions MUST NOT become effective merely because the descriptor contains them.

A descriptor MAY narrow capabilities temporarily.

Example:

```text
signed Tilden: video + audio + rtt
current descriptor: video + rtt

effective: video + rtt
```

This allows a service to remove a temporarily unavailable modality without allowing dynamic unsigned metadata to enlarge the signed outer claim.

## 12. Transport records

Each transport record MUST contain:

- `id` — stable identifier within the descriptor;
- `type` — transport family;
- `uri` — transport-specific target;
- `priority` — preference within this Baudot service, lower values preferred;
- `media` — media available through the transport.

A transport MAY contain:

- `features` — feature tokens;
- `profiles` — protocol/profile tokens;
- `metadata` — extension data.

Transport priority is subordinate to the parent Tilden capability priority.

A transport record MUST NOT alter the priority of another top-level Tilden capability.

## 13. Initial transport types

The initial binding defines:

| Type | Meaning |
| --- | --- |
| `sip` | SIP-family session establishment using the transport URI |
| `webrtc` | WebRTC-capable service entry point; application signaling remains service-defined |

Future specifications MAY define additional transport types.

Unknown transport types MUST be ignored unless explicitly required by caller policy.

## 14. Initial profile tokens

### 14.1 `t140-rfc4103`

The transport carries T.140 real-time text using the RTP payload format defined by RFC 4103.

When RFC 4103 is used, implementations MUST follow its applicable packetization, sequencing, SDP, and loss-protection requirements. The default RFC 4103 loss-protection behavior uses RFC 2198 redundancy unless another method is explicitly selected under the RFC's rules.

Advertising this token does not by itself prove conformance. It is a protocol support assertion subject to implementation evidence and interoperability testing.

### 14.2 `t140-rfc8865`

The transport carries T.140 real-time text over a WebRTC data channel according to RFC 8865.

RFC 8865 uses reliable WebRTC data-channel transport rather than RFC 4103 RTP redundancy.

Advertising `t140-rfc8865` MUST NOT be interpreted as advertising `t140-rfc4103`, and vice versa.

### 14.3 `rue-rfc9248`

A SIP transport MAY advertise:

```text
rue-rfc9248
```

when it intentionally implements the Relay User Equipment interoperability profile defined by RFC 9248.

This is a strong interoperability assertion. Deployments SHOULD NOT advertise `rue-rfc9248` merely because they use SIP, video, or T.140.

Tilden and Baudot do not certify RFC 9248 conformance.

## 15. Modality requirements

A caller MAY require one or more media classes or features before attempting the call.

Example caller policy:

```json
{
  "require_media": ["video", "rtt"],
  "require_features": ["asl", "t140"]
}
```

A transport is eligible only when its effective capability set satisfies the caller's requirements.

A client SHOULD prefer an eligible transport with the lowest transport priority.

Local policy MAY consider additional factors such as privacy, cost, reliability, or user preference after mandatory accessibility requirements are satisfied.

## 16. No silent accessibility downgrade

A failed Baudot attempt MUST NOT silently degrade to a transport that violates an explicit modality requirement.

Example:

```text
required: video + RTT

Baudot video + RTT fails
PSTN audio remains available

result: do not silently place audio-only PSTN call
```

A client MAY offer the user an explicit fallback when policy allows it.

If no modality requirement was expressed, local policy MAY select another Tilden capability according to CORE-001 priority and user preferences.

Accessibility requirements take precedence over convenience fallback.

## 17. Runtime readiness

Discovery metadata describes capability. Runtime observations establish readiness.

The initial reference descriptor uses:

```text
baudot.modality-readiness@1
```

The following invariants apply when the corresponding modalities are required.

### 17.1 RTT readiness

RTT MUST NOT be considered ready solely because SDP or another negotiation mechanism advertised text.

For the reference readiness contract:

```text
rttReady = rttNegotiated
           AND firstT140CharacterObserved
```

A deployment MAY use an equivalent independently observable T.140 readiness event where the exact first-character probe is not appropriate, but it MUST NOT collapse negotiation and observed text flow into one fact.

### 17.2 Video readiness

Where rendered video is required for usable sign-language communication, signaling or inbound packets alone are insufficient.

The reference contract distinguishes at least:

```text
videoInbound
videoDecoded
videoRendered
```

A client MUST NOT claim rendered-video readiness from signaling success alone.

### 17.3 Audio readiness

Where audio is required, a client SHOULD distinguish negotiated audio from observed usable audio flow.

Future Baudot contracts MAY define stronger audio readiness evidence.

## 18. Transfer and handoff

A session transfer, replacement dialog, migration, or provider handoff creates a new readiness decision.

The new leg MUST NOT inherit accessibility readiness merely because the old leg was ready.

For continuity-sensitive handoff:

```text
old leg ready
      |
      +---- replacement signaling succeeds
      |
      +---- replacement media negotiated
      |
      +---- replacement required modalities observed ready
      |
      v
old leg may be released
```

When RTT is required, a successful REFER/NOTIFY sequence or replacement dialog is insufficient until RTT readiness is independently established.

This is intentionally aligned with Baudot's provider-neutral transfer model in `BAUDOT-INTEROP-004`.

## 19. Session identity correlation

Tilden authorizes discovery of the destination service. Session protocols remain responsible for their own peer and media authentication.

When a transport exposes a destination identity, implementations SHOULD correlate it with the Tilden subject when the protocol makes such correlation meaningful.

A successful Tilden resolution MUST NOT cause a client to ignore a conflicting transport-level identity.

This profile does not define caller identity authentication.

## 20. Descriptor freshness

Baudot Service Descriptors SHOULD be short-lived because transport availability can change more rapidly than telephone identity authority.

A client MUST NOT use an expired descriptor to begin a new session unless explicit offline policy allows degraded operation.

The descriptor expiration MUST NOT extend the validity of the parent Tilden Resolution Object.

Effective validity ends at the earliest of:

- parent Tilden Resolution Object expiration;
- parent authority revocation or transfer;
- descriptor expiration;
- local policy limit.

## 21. Caching

A client MAY cache a valid descriptor until its effective validity ends.

A cached descriptor MUST remain bound to the exact parent Tilden subject and service URI from which it was derived.

A client MUST NOT reuse a descriptor for another telephone number merely because the same service origin hosts both numbers.

## 22. Failure classes

Implementations SHOULD distinguish at least:

- `parent-resolution-invalid` — the Tilden object is not currently trusted;
- `baudot-not-advertised` — no Baudot capability exists;
- `descriptor-unavailable` — the service resource cannot be retrieved;
- `descriptor-invalid` — descriptor syntax or required fields are invalid;
- `subject-mismatch` — descriptor subject differs from the Tilden subject;
- `service-uri-mismatch` — descriptor is not bound to the selected capability URI;
- `descriptor-expired` — descriptor is stale;
- `no-compatible-transport` — no transport satisfies mandatory media/features;
- `transport-failed` — session establishment failed;
- `readiness-not-achieved` — signaling or transport connected but required runtime modality evidence did not become true;
- `downgrade-blocked` — a lower capability exists but violates explicit accessibility policy.

These outcomes SHOULD remain distinct in evidence and telemetry.

## 23. Fallback

Failure of a Baudot service does not prove the Tilden subject is unreachable.

A client MAY evaluate the next Tilden capability when:

1. local policy permits fallback; and
2. the fallback satisfies all mandatory modality and security requirements.

Example:

```text
Baudot transport failure
       |
       +-- SIP capability supports required video + RTT -> MAY try
       |
       +-- VRS capability satisfies caller policy       -> MAY try
       |
       +-- PSTN audio only, but RTT required            -> MUST NOT silently try
```

## 24. Privacy

A descriptor SHOULD publish only information required for interoperability.

It MUST NOT expose:

- private subscriber credentials;
- eSIM activation secrets;
- IMSI or ICCID values;
- private SIP passwords;
- WebRTC ephemeral secrets before an authenticated session requires them;
- Apple Account identifiers;
- unnecessary disability or medical information.

Capability metadata SHOULD describe the endpoint rather than label the person.

## 25. Security

Implementations MUST consider at least:

### 25.1 Descriptor substitution

An attacker substitutes a descriptor for another Tilden subject.

**Mitigation:** exact `subject` and `service_uri` binding plus authenticated HTTPS.

### 25.2 Capability expansion

A compromised dynamic service advertises capabilities beyond the signed Tilden record.

**Mitigation:** effective media/features are intersections with the parent signed capability.

### 25.3 Cross-origin redirect

The authorized service redirects discovery to an unrelated origin.

**Mitigation:** cross-origin authority is not inherited from HTTP redirection.

### 25.4 Downgrade attack

An attacker causes the preferred accessible transport to fail so the client falls back to an unusable audio-only path.

**Mitigation:** explicit modality requirements and no silent accessibility downgrade.

### 25.5 False readiness

A transport reports signaling success before required media is usable.

**Mitigation:** runtime readiness is reduced from independent evidence, not connection state alone.

### 25.6 Stale handoff

A replacement leg is promoted before required modalities are usable.

**Mitigation:** new-leg readiness is established before old-leg teardown under continuity policy.

## 26. Reference selection algorithm

Given a verified Tilden Resolution Object and caller requirements:

1. select an eligible `baudot` capability using Tilden priority and policy;
2. retrieve its Baudot Service Descriptor over authenticated HTTPS;
3. validate subject, service URI, freshness, and parent authority;
4. for each transport, calculate effective media/features as the intersection with the parent capability;
5. discard transports that fail mandatory requirements;
6. order remaining transports by descriptor transport priority;
7. attempt the preferred transport;
8. preserve signaling, connection, media, and readiness observations as separate facts;
9. declare the call usable only when required modality readiness is established;
10. on failure, apply explicit fallback policy without violating accessibility requirements.

## 27. Reference example

The repository reference vector pairs:

```text
examples/resolution.json
        |
        +-- signed by examples/signed-resolution.jws.json
        |
        +-- baudot capability URI
                    |
                    v
examples/baudot-service.json
```

`examples/validate-baudot-binding.mjs` verifies the static binding invariants and negative subject/downgrade cases.

## 28. Relationship to Baudot implementation evidence

Tilden describes where a Baudot-capable service may be found.

Baudot remains responsible for proving behavior at the semantic and interoperability boundary.

In particular:

```text
Tilden says: this service is authorized and advertises RTT.
Baudot asks: was T.140 actually negotiated and observed?
```

This separation is intentional.

A Tilden capability is routing evidence.

A Baudot runtime observation is usability evidence.

Neither substitutes for the other.

## 29. Normative references

This profile relies on the applicable requirements of:

- TILDEN-CORE-001;
- TILDEN-AUTH-003;
- TILDEN-SIGN-004;
- RFC 4103, RTP Payload for Text Conversation;
- RFC 2198, RTP Payload for Redundant Audio Data, when used by RFC 4103;
- RFC 8865, T.140 Real-Time Text Conversation over WebRTC Data Channels;
- RFC 9248, Interoperability Profile for Relay User Equipment, when `rue-rfc9248` is advertised.

## 30. Reference statement

The complete reference path is:

```text
one number
   -> authenticated Tilden authority
   -> signed capability set
   -> Baudot service discovery
   -> compatible transport selection
   -> observed modality readiness
   -> usable conversation
```

The governing user-facing principle remains:

> **One number. Every modality.**
