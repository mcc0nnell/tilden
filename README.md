# Tilden

**Federated identity, addressing, discovery, and capability resolution for accessible real-time communications.**

Tilden defines a neutral resolution layer for accessible calling. It maps human-reachable identifiers to authoritative federation endpoints and capability metadata without requiring the world to adopt a single provider or calling stack.

Baudot is expected to be the first reference consumer of Tilden resolution objects, but Tilden is intentionally independent of Baudot.

> **One number. Every modality.**

## The invariant

```text
NUMBER != NETWORK
```

A telephone number can be the stable rendezvous identity without requiring every conversation to use the telephone network.

```text
                    +1 202 555 0123
                       Tilden identity
                              |
              +---------------+---------------+
              |                               |
       Tilden resolution                carrier identity
              |                               |
      +-------+--------+                     eSIM
      |       |        |                      |
     SIP     RTT     Baudot             PSTN / SMS / native
      |       |        |                 platform services
     VRS    text    federation
```

Tilden resolves identity to capability. The selected communications system then establishes the session.

## Specifications

- [`TILDEN-CORE-001`](spec/TILDEN-CORE-001.md) — identity, discovery, and capability resolution
- [`TILDEN-ESIM-002`](spec/TILDEN-ESIM-002.md) — optional carrier-backed eSIM identity binding
- [`TILDEN-AUTH-003`](spec/TILDEN-AUTH-003.md) — authenticated resolver authority and bootstrap
- [`TILDEN-SIGN-004`](spec/TILDEN-SIGN-004.md) — signed Resolution Objects and current-authority verification
- [`TILDEN-BAUDOT-005`](spec/TILDEN-BAUDOT-005.md) — Baudot service discovery, modality-safe transport selection, and readiness binding

See the complete [`spec/`](spec/) index.

## Resolution object

A Tilden resolver returns a short-lived description of authorized ways to reach an identity:

```json
{
  "tilden_version": "1",
  "subject": "tel:+12025550123",
  "issued_at": "2026-09-05T21:00:00Z",
  "expires_at": "2026-09-05T21:15:00Z",
  "authority": "https://resolver.example.net",
  "capabilities": [
    {
      "type": "baudot",
      "uri": "https://baudot.example.net/call/+12025550123",
      "priority": 10,
      "media": ["video", "audio", "rtt"],
      "features": ["asl", "direct", "t140"]
    },
    {
      "type": "pstn",
      "uri": "tel:+12025550123",
      "priority": 100,
      "media": ["audio"]
    }
  ]
}
```

The machine-readable schema is [`schemas/tilden-resolution-v1.schema.json`](schemas/tilden-resolution-v1.schema.json), with a fuller reference object in [`examples/resolution.json`](examples/resolution.json).

## Trust chain

TLS can prove that a client reached `resolver.example.net`; it cannot prove that the resolver is allowed to speak for a particular telephone number. Tilden therefore separates origin authentication, subject authority, and object integrity:

```text
identity
  -> authenticated bootstrap
  -> subject delegation
  -> authorized resolver + signing key
  -> verified Resolution Object
  -> selected endpoint
  -> independently authenticated session
```

`TILDEN-AUTH-003` establishes resolver and signing-key authority. `TILDEN-SIGN-004` uses that delegated key to sign the Resolution Object with Ed25519 JWS.

A cryptographically valid signature is not enough by itself. Clients verify the signer against the **current** accepted delegation state, so revocation, number reassignment, and resolver transfer can invalidate still-unexpired cached objects.

Reference objects:

- [`examples/authority-delegation.json`](examples/authority-delegation.json)
- [`examples/signed-resolution.jws.json`](examples/signed-resolution.jws.json)

## Reference HTTPS profile

The first reference resolver profile is intentionally small enough to run on ordinary edge infrastructure, including a serverless worker:

```http
GET /.well-known/tilden/v1/resolve?subject=tel%3A%2B12025550123
Accept: application/tilden+json, application/tilden-resolution+jws
```

The worker is not the phone network. It is the authorized resolution service that tells a client which networks or endpoints are available.

## Baudot binding

`TILDEN-BAUDOT-005` gives the signed `baudot` capability an exact meaning.

```text
verified Tilden number
       |
       v
signed baudot service URI
       |
       v
Baudot Service Descriptor
       |
       +-- SIP + T.140/RFC 4103
       |
       +-- WebRTC + T.140/RFC 8865
       |
       +-- optional RUE/RFC 9248 profile
       |
       v
observed modality readiness
```

The outer Tilden record selects an authorized service. The dynamic Baudot descriptor chooses among transports but may only **narrow** the signed media/features, never expand them.

The binding also preserves Baudot's critical runtime distinction:

```text
signaling success != usable communication
```

For the reference RTT readiness contract, negotiation alone is insufficient. `rttReady` requires both `rttNegotiated` and independent observation of T.140 flow.

If an explicit caller policy requires video + RTT, failure of that accessible path does **not** silently authorize fallback to an audio-only PSTN call.

Reference descriptor and executable vector:

- [`examples/baudot-service.json`](examples/baudot-service.json)
- [`examples/validate-baudot-binding.mjs`](examples/validate-baudot-binding.mjs)

## eSIM profile

`TILDEN-ESIM-002` allows the same E.164 identity to be legitimately bound to a carrier eSIM while remaining independently resolvable through Tilden.

That creates a clean separation:

```text
identity -> resolution -> endpoint -> session
```

Carrier service, SIP, RTT, VRS, Baudot, and platform-native communications can coexist behind the same human-facing number without Tilden pretending to implement or bypass any proprietary platform.

## Project status

Tilden is an early protocol design. The current work is defining the smallest trustworthy resolution model first, then adding narrowly scoped interoperability profiles around it.
