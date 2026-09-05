# ADR 0004: Capabilities are pre-session semantics, not session negotiation

Status: Accepted for Draft 0.1

## Context

Tilden needs to advertise accessibility-relevant communication capabilities before a session is established. Existing runtime protocols already negotiate codecs, transports, ports, security parameters, and offer/answer state.

Duplicating that space inside Tilden would create a second signaling protocol, increase drift, and couple federation discovery to specific media stacks.

## Decision

Tilden capability identifiers describe stable, pre-session communication semantics such as signed-language video, real-time text, captions, interpreted relay, multimodal participation, accessible transfer, and end-to-end encryption support.

Capability parameters may refine those semantics, including language or documented runtime-profile references, but MUST NOT reproduce transient session-description state.

Codec lists, ICE candidates, DTLS fingerprints, RTP payload bindings, ports, SSRCs, and offer/answer state remain runtime concerns.

The capability registry is machine-readable and independently validated. Unknown standard-looking IDs are not assumed to be supported; experimental extensions use the `x.` namespace until promoted.

## Consequences

Tilden remains implementation-neutral and useful across SIP, WebRTC, and future runtimes.

Baudot can use Tilden capabilities to select plausible endpoints, while retaining full responsibility for actual session negotiation and interoperability evidence.

The registry can evolve without forcing changes to media signaling protocols.
