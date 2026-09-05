# Tilden next specifications

The core control-plane slice is now defined. The next work should stay narrow and profile-oriented.

## TILDEN-E164-001 — E.164 authority bootstrap

Define how a relying party moves from a normalized `tel:+...` identifier to a verifiable Tilden delegation.

Questions:

- What existing numbering or portability authority is authoritative enough to bootstrap Tilden?
- Can DNS participate without becoming the legal source of number control?
- How are carrier and non-carrier resolver operators represented?
- How quickly must a port or revocation propagate?

## TILDEN-CAP-001 — Capability registry

Define stable machine-readable tokens for endpoint capabilities without encoding disability identity.

Candidate classes:

- media: `audio`, `video`, `text`;
- transport: `sip`, `webrtc`, `rtt`, `pstn`;
- interaction: `asl`, `captions`, `relay`, `direct-video`;
- security: `e2ee`, authenticated caller, federation assurance.

The registry must describe endpoint behavior, not infer personal attributes.

## TILDEN-FED-001 — Federation trust

Define authenticated resolver-to-resolver and gateway-to-resolver relationships, including trust anchors, key rotation, policy domains, and cross-provider verification.

## TILDEN-PRIV-001 — Private resolution

Define privacy-preserving queries where a resolver can answer “here is a compatible route” without publishing the user's full endpoint inventory or accessibility preferences.

## TILDEN-EMERG-001 — Emergency communications

Emergency calling must be handled explicitly rather than inheriting ordinary Tilden routing assumptions.

This profile should address jurisdiction, location, fallback behavior, PSAP routing, relay involvement, and failure modes.

## Reference implementation

Once `TILDEN-E164-001` has a plausible bootstrap, build the smallest possible reference implementation:

```text
Cloudflare Worker
  + static or KV-backed delegation
  + signed resolution object
  + one SIP endpoint
  + one WebRTC endpoint
  + conformance fixtures
```

The reference implementation should prove the protocol boundary, not become the protocol definition.
