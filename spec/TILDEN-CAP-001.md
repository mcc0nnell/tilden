# TILDEN-CAP-001: Accessible Calling Capability Vocabulary

Status: **Draft 0.1**  
Specification ID: `TILDEN-CAP-001`

## 1. Purpose

Tilden capabilities describe what an endpoint or identity asserts it can support for accessible real-time communications before session establishment. They are discovery metadata, not a replacement for SDP, SIP, WebRTC, RTP, RTT, or other runtime negotiation.

The goal is to make accessibility-relevant reachability machine-readable across independently operated providers, enterprises, national networks, and runtimes.

## 2. Design principle

Tilden capabilities answer:

> What communication service can this endpoint plausibly provide?

Runtime protocols answer:

> Can the two endpoints negotiate the exact media, codecs, transports, and security parameters for this session?

A Tilden capability assertion MUST NOT be interpreted as proof that session negotiation will succeed.

## 3. Capability shape

Capabilities use the object shape already defined by `TILDEN-CORE-001`:

```json
{
  "id": "text.rtt",
  "parameters": {
    "languages": ["en"]
  }
}
```

The `id` defines semantics. `parameters` refine the assertion but MUST NOT redefine the capability.

## 4. Namespace rules

Standard Tilden capability identifiers are lowercase dotted names.

Initial top-level namespaces are:

- `audio.*`
- `video.*`
- `text.*`
- `relay.*`
- `security.*`
- `transfer.*`
- `session.*`

Private extensions SHOULD use a reverse-domain-style prefix under `x.` such as `x.example.feature` and MUST NOT collide with standard capability IDs.

## 5. Initial standard capability registry

### 5.1 `audio.voice`

The endpoint can participate in bidirectional conversational audio.

Optional parameters:

- `languages`: BCP 47 language tags for spoken-language support where meaningful;
- `direction`: `sendrecv`, `sendonly`, or `recvonly`.

Codec selection is intentionally excluded and belongs to runtime negotiation.

### 5.2 `video.sign`

The endpoint can participate in bidirectional video intended to support signed-language communication.

Optional parameters:

- `languages`: BCP 47 language tags identifying signed languages where known;
- `direction`: `sendrecv`, `sendonly`, or `recvonly`.

Implementations SHOULD use specific language subtags, such as `ase` for American Sign Language, rather than the generic `sgn` family tag when a specific language is known.

`video.sign` does not imply any particular codec, frame rate, resolution, camera layout, or RTP/WebRTC profile.

### 5.3 `text.rtt`

The endpoint can participate in conversational real-time text.

Optional parameters:

- `languages`: BCP 47 language tags when the text language is known;
- `profile`: a registered or documented runtime profile identifier.

For RTP-based sessions, RFC 4103 `text/t140` is a relevant runtime mechanism, but Tilden does not require RFC 4103 for every implementation.

### 5.4 `text.caption`

The endpoint can provide or consume captions synchronized to a real-time session.

Optional parameters:

- `languages`: BCP 47 caption languages;
- `mode`: `provided`, `requested`, or `bidirectional`.

This capability does not state how captions are generated or transported.

### 5.5 `relay.interpreter`

The endpoint exposes interpreted relay participation as part of the reachable service.

Optional parameters:

- `sourceLanguages`: BCP 47 language tags;
- `targetLanguages`: BCP 47 language tags;
- `modalities`: values such as `sign-video`, `voice`, or `text-rtt`.

This capability describes service availability only. It does not assert regulatory eligibility, funding status, interpreter certification, or billing treatment.

### 5.6 `relay.captioning`

The endpoint exposes a relay-mediated captioning service.

Optional parameters:

- `languages`: BCP 47 language tags;
- `input`: values such as `audio.voice`;
- `output`: values such as `text.caption` or `text.rtt`.

### 5.7 `security.e2ee`

The endpoint advertises support for at least one end-to-end encrypted session profile in which intermediary federation infrastructure does not possess session plaintext solely by virtue of routing the call.

Optional parameters:

- `profiles`: documented session-security profile identifiers.

The exact cryptographic negotiation remains a runtime responsibility. Consumers MUST NOT infer E2EE merely from hop-by-hop TLS.

### 5.8 `transfer.accessible`

The endpoint supports transfer or redirection without intentionally discarding the accessibility modalities active for the session.

Optional parameters:

- `preserves`: capability identifiers the endpoint claims it can preserve across transfer.

Runtime success still depends on the destination endpoint.

### 5.9 `session.multimodal`

The endpoint can support more than one concurrent conversational modality in the same logical call, such as video plus RTT plus audio.

Optional parameters:

- `combinations`: arrays of capability IDs known to be supported concurrently.

This is distinct from asserting each modality independently: independent support does not always prove concurrent support.

## 6. Language tagging

When capabilities carry language metadata, implementations SHOULD use BCP 47 language tags.

Specific signed languages SHOULD use their specific registered language subtags where available. The generic `sgn` subtag indicates sign language in general and SHOULD NOT replace a known specific language.

Language preference negotiation, interpretation direction, and user preference policy remain outside the core capability registry.

## 7. Runtime media details

Tilden MUST NOT attempt to mirror the complete session-description space.

The following normally belong to SDP, WebRTC, SIP, RTP, or another runtime mechanism rather than Tilden capability IDs:

- codec payload types;
- ICE candidates;
- DTLS fingerprints;
- SRTP keys;
- RTP SSRC values;
- packetization parameters;
- exact media ports;
- offer/answer state;
- transient bandwidth measurements.

A capability profile MAY reference a documented runtime profile, but it MUST NOT turn Tilden into an offer/answer protocol.

## 8. Identity-level and endpoint-level capabilities

A `TildenResolution` MAY contain capabilities at both identity and endpoint scope.

Identity-level capabilities mean at least one authoritative route for the identity claims the capability.

Endpoint-level capabilities describe that specific route.

When the two differ, consumers MUST use endpoint-level capability data when selecting that endpoint and MUST NOT promote an identity-level assertion into an unsupported endpoint-level assertion.

## 9. Matching semantics

Capability matching is conjunctive by default:

- a caller requirement is satisfied only if the selected endpoint asserts every capability marked as required by local policy;
- optional capabilities MAY improve endpoint ranking;
- unknown capability IDs MUST NOT be treated as supported;
- unknown parameters MUST NOT alter the semantics of a known standard capability.

Tilden selection produces a candidate endpoint. Baudot or another runtime remains responsible for actual negotiation.

## 10. Privacy

Accessibility capability metadata can reveal disability, language, relay usage, or communication preferences.

Resolvers SHOULD publish the minimum capability detail needed to route and establish a session. Public directory records SHOULD prefer service-level capability assertions over unnecessary user-specific preference disclosure.

Language lists SHOULD be omitted when they are not necessary for routing or pre-session selection.

## 11. Extensibility and registry governance

New standard capability IDs require:

1. a stable semantic definition;
2. evidence that the property is useful before session establishment;
3. a clear boundary from runtime protocol negotiation;
4. privacy considerations;
5. at least one interoperable implementation or executable fixture before promotion from experimental status.

Experimental extensions SHOULD use `x.` identifiers until accepted into the standard registry.

## 12. Conformance

A conforming producer MUST:

1. emit syntactically valid capability IDs;
2. use standard IDs according to their defined semantics;
3. avoid advertising codec/session parameters as standalone accessibility capabilities;
4. avoid asserting `security.e2ee` for hop-by-hop transport security alone;
5. use endpoint-level data when an endpoint differs from identity-level capabilities.

A conforming consumer MUST:

1. treat unknown capability IDs as unsupported unless local extension policy says otherwise;
2. never infer session success solely from capability discovery;
3. enforce required capability matching before handing a candidate to the runtime;
4. retain enough evidence to explain why an endpoint was selected or rejected.

## 13. Relationship to existing standards

Tilden reuses established standards rather than redefining them:

- BCP 47 / RFC 5646 for language tagging;
- RFC 4103 for RTP real-time text using `text/t140` where that runtime profile applies;
- SDP as standardized in RFC 8866 for runtime media/session descriptions.

Tilden capabilities remain higher-level pre-session discovery metadata.

## 14. Open questions

Draft 0.1 deliberately leaves open:

- whether capability IDs need a formal IANA-style registry or project-governed registry first;
- whether language direction belongs in capability parameters or a later preferences profile;
- whether emergency accessibility capabilities belong in this registry or a dedicated emergency profile;
- whether `relay.interpreter` should later split into finer service classes;
- how much multimodal combination detail is safe and useful to publish;
- whether a mandatory baseline capability set is appropriate for federation membership.
