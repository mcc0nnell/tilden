# ADR-0001: Tilden resolution is control plane, not media plane

**Status:** Accepted for initial architecture

## Context

Tilden needs to map a durable communications identity to the current set of endpoints capable of receiving communications for that identity.

A tempting implementation is to make the numbering layer also terminate SIP, relay WebRTC, transcode media, or otherwise become part of every call path. That would couple numbering to transport details, increase operational and security scope, and make new communications protocols harder to add.

The project also needs to permit lightweight edge implementations. An E.164 identifier, for example, could resolve through an HTTPS function running on Cloudflare Workers or another edge platform even when the actual call is completed over SIP, VRS, RTT, WebRTC, PSTN, or a native calling service.

## Decision

Tilden is a **communications resolution control plane**.

A Tilden resolver:

- receives a normalized communications identifier;
- determines the authoritative routing policy;
- evaluates endpoint and session capabilities;
- returns one or more ordered destinations;
- may return authorization or rendezvous material needed to establish a session.

A Tilden resolver does **not** need to:

- carry media;
- terminate SIP dialogs;
- relay RTP;
- transcode media;
- implement VRS;
- act as a WebRTC media server.

Media and signaling may flow directly between endpoints or through separate interoperability components after Tilden resolution completes.

Cloudflare Workers, Durable Objects, or similar services are valid implementation choices, but no Tilden protocol element may require a Cloudflare-specific API.

## Consequences

### Positive

- A phone number can behave as a programmable routing identity without turning Tilden into a telephone switch.
- Numbering remains stable when providers, devices, applications, or transports change.
- Tilden can be implemented using small HTTPS edge functions.
- The attack surface of the core resolver is substantially smaller than a media gateway.
- New transports can be added through endpoint and capability definitions rather than core architectural changes.
- Baudot can consume Tilden results while retaining responsibility for protocol interoperability.

### Tradeoffs

- A separate ingress or gateway is still required when legacy networks cannot perform Tilden resolution directly.
- End-to-end session establishment errors occur outside the resolver and need separate observability.
- Capability claims and routing metadata require clear authority, privacy, and integrity rules.

## Boundary

The architectural boundary is intentionally simple:

> **Tilden decides where and how an identity can be reached. Baudot and other transports decide how the resulting communication is established.**
