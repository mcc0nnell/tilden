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

## Reference HTTPS profile

The first reference resolver profile is intentionally small enough to run on ordinary edge infrastructure, including a serverless worker:

```http
GET /.well-known/tilden/v1/resolve?subject=tel%3A%2B12025550123
Accept: application/tilden+json
```

The worker is not the phone network. It is the resolution authority that tells an authorized client which networks or endpoints are available.

## eSIM profile

`TILDEN-ESIM-002` allows the same E.164 identity to be legitimately bound to a carrier eSIM while remaining independently resolvable through Tilden.

That creates a clean separation:

```text
identity -> resolution -> endpoint -> session
```

Carrier service, SIP, RTT, VRS, Baudot, and platform-native communications can coexist behind the same human-facing number without Tilden pretending to implement or bypass any proprietary platform.

## Project status

Tilden is an early protocol design. The current work is defining the smallest trustworthy resolution model first, then adding narrowly scoped interoperability profiles around it.
