# Architecture

Tilden is the identity, addressing, discovery, trust, capability-selection, and routing-evidence layer for federated accessible calling.

```text
Human-reachable identifier
  |  tel:+12025550123
  |  provider-independent URI
  |  enterprise/national identity
  v
Tilden discovery + trust
  |- normalization
  |- authority/delegation
  |- discovery
  |- capability advertisement
  |- trust + freshness
  v
TildenResolution
  +
TildenRequest (ephemeral, caller-side)
  |- required capabilities
  |- preferred capabilities
  |- excluded routes/capabilities
  |- short lifetime
  v
Tilden selection
  |- deterministic filtering
  |- preference scoring
  |- deterministic tie-breaking
  |- evidence generation
  v
TildenSelection
  |- selected endpoint
  |- resolution/request digests
  |- candidate outcomes
  `- terminal result
  v
Consumer
  |- Baudot reference runtime
  |- independent SIP/WebRTC gateway
  |- national relay network
  `- enterprise communications platform
```

## Boundary rule

**Tilden answers who, where, and how an identity can be reached, then records why a particular endpoint is the best candidate for one call. It does not prove that two implementations can successfully establish a session.**

Baudot begins after selection. It may use the selected endpoint and validated resolution context to attempt session establishment, negotiate signaling/media, enforce runtime policy, and generate interoperability evidence.

## Dependency direction

```text
Baudot ---> Tilden contracts
Tilden -X-> Baudot runtime
```

Tilden specifications, schemas, and reference tooling must remain usable without Baudot.

## Evidence flow

```text
TildenDiscoveryTrace
        |
        v
TildenResolution ----+
                     |
TildenRequest -------+--> TildenSelection ---> Baudot runtime evidence
                                             |
                                             v
                                      assurance / WindAnvil
```

Selection evidence binds to the exact resolution and request by digest rather than embedding the full caller request. That supports reproducibility while reducing unnecessary persistence of accessibility preferences.

## Reference executable

The reference CLI under `src/tilden/` executes the current architecture without pretending that global network discovery already exists:

```text
tilden resolve   -> deterministic reference directory -> TildenResolution
tilden request   -> short-lived caller requirements   -> TildenRequest
tilden select    -> deterministic selection           -> TildenSelection
tilden explain   -> human-readable evidence
```

The reference directory is a test adapter. ENUM, WebFinger, HTTPS, directories, and other discovery mechanisms remain adapters governed by `TILDEN-DISCOVERY-001` and future profiles.

## Federation invariant

No Tilden design should require all accessible callers or providers to join one commercial platform. Multiple authorities, resolver implementations, transports, trust profiles, and national networks must be able to participate under interoperable profiles.

## Privacy invariant

Accessibility metadata may be sensitive. Resolution should disclose the minimum capability information needed for routing. Per-call requirements should remain ephemeral and caller-side unless a later profile explicitly defines selective disclosure. Evidence artifacts should favor digests and capability IDs over copying private request parameters.
