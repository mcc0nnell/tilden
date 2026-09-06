# Architecture

Tilden is the identity, addressing, discovery, and routing-resolution layer for federated accessible calling.

```text
Human-reachable identifier
  |  tel:+12025550123
  |  provider-independent URI
  |  enterprise/national identity
  v
Tilden
  |- normalization
  |- authority/delegation
  |- discovery
  |- capability advertisement
  |- trust + freshness
  `- endpoint selection inputs
  v
TildenResolution
  v
Consumer
  |- Baudot reference runtime
  |- independent SIP/WebRTC gateway
  |- national relay network
  `- enterprise communications platform
```

## Boundary rule

**Tilden answers who, where, and how an identity can be reached. It does not prove that two implementations can successfully establish a session.**

Baudot begins after resolution. It may use Tilden results to attempt session establishment, negotiate signaling/media, enforce runtime policy, and generate interoperability evidence.

## Dependency direction

```text
Baudot ---> Tilden contract
Tilden -X-> Baudot runtime
```

Tilden specifications and schemas must remain usable without Baudot.

## Federation invariant

No Tilden design should require all accessible callers or providers to join one commercial platform. Multiple authorities, resolver implementations, transports, trust profiles, and national networks must be able to participate under interoperable profiles.

## Privacy invariant

Accessibility metadata may be sensitive. Resolution should disclose the minimum capability information needed for successful routing and negotiation, and designs should resist bulk enumeration of user identities.
