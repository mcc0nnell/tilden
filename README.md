# Tilden

**Federated identity, addressing, discovery, and capability resolution for accessible real-time communications.**

Tilden defines a neutral resolution layer for accessible calling. It maps human-reachable identifiers to authoritative federation endpoints and capability metadata without requiring the world to adopt a single provider or calling stack.

> **A Tilden number is a persistent communications identity whose current network destination is resolved programmatically.**

A telephone number can therefore remain stable while the provider, application, device, transport, or accessibility service behind it changes.

```text
E.164 number
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

## The boundary

**Tilden answers:** Where and how should this communications identity be reached?

**Baudot answers:** How do the selected communications systems interoperate?

Tilden is a naming, discovery, capability, and routing **control plane**. It does not need to terminate or transport the media session.

Baudot is expected to be the first reference consumer of Tilden resolution objects, but Tilden is intentionally independent of Baudot.

## Edge implementation

A Tilden resolver can be very small. An E.164 identifier could, for example, resolve through an HTTPS edge function implemented with Cloudflare Workers or an equivalent runtime.

That function can evaluate authority, endpoints, accessibility capabilities, authorization, and routing policy, then return an ordered set of destinations. The actual call can proceed over SIP, VRS, WebRTC, RTT, PSTN, native video calling, or another transport without media traversing Tilden.

Cloudflare is an implementation profile, not a protocol dependency.

## Specification

- [`TILDEN-CORE-001`](spec/TILDEN-CORE-001.md) — programmable number resolution and core architecture
- [`ADR-0001`](docs/adr/0001-resolution-is-control-plane.md) — resolution is control plane, not media plane
- [`tilden-resolution-v0.1.schema.json`](schemas/tilden-resolution-v0.1.schema.json) — initial machine-readable resolution object

## Design principles

- Stable identity, replaceable transport.
- Resolution is separate from media.
- Accessibility capabilities are first-class routing inputs.
- Providers and applications are endpoints, not owners of identity.
- Federation must not require one global operator.
- Existing E.164 and SIP infrastructure remains usable as ingress and fallback.
- Vendor-specific edge services may implement Tilden, but must not define Tilden.
