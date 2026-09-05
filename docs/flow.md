# Tilden call-resolution flow

Tilden is a control-plane protocol. Its job ends when a relying party has a current, authoritative set of candidate communications endpoints.

```text
Human-facing identifier
        |
        |  e.g. +1 202 555 0142
        v
Normalize identifier
        |
        |  tel:+12025550142
        v
Discover authority
        |
        v
Validate delegation
        |
        |  authority -> resolver
        v
Resolve capabilities and routes
        |
        |  HTTPS Tilden request
        v
Validate signed resolution object
        |
        v
Select compatible endpoint
        |
        +--------------------+--------------------+-------------------+
        |                    |                    |                   |
        v                    v                    v                   v
       SIP                 WebRTC                RTT                 VRS
        |                    |                    |                   |
        +--------------------+--------------------+-------------------+
                                     |
                                     v
                            Signaling / Baudot
                                     |
                                     v
                                  Media
```

## The boundary

Tilden does not switch the call and does not require media to traverse the resolver.

The simplest mental model is:

> **Resolve first. Connect second.**

A Cloudflare Worker can implement the resolution step because that step is ordinary authenticated control-plane computation: accept a request, evaluate policy, and return a signed routing object.

## Why this matters

The model lets a telephone number remain stable while the reachable communications path changes underneath it.

A user could move among:

- carriers;
- VRS providers;
- SIP services;
- native video services;
- WebRTC applications;
- RTT endpoints;
- future communications platforms;

without changing the Tilden identity itself.

Provider changes alter delegation and routing state, not the identifier.
