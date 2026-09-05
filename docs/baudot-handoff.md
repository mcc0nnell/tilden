# Baudot handoff

Tilden now hands Baudot a selected route plus evidence, not merely a raw resolution object.

```text
TildenResolution
  +
TildenRequest (caller-side)
        |
        v
Tilden selection
        |
        v
TildenSelection
  |- selectionId
  |- selectedEndpoint
  |- resolutionDigest
  |- requestDigest
  |- candidate outcomes
  `- terminal result
        |
        v
Baudot policy gate
        |
        +-- reject: trust/local policy/conformance failure
        |
        `-- accept selected endpoint
              |
              v
        session negotiation
        SIP / WebRTC / RTT / video / other adapters
```

## What Baudot should consume

At minimum, Baudot needs:

- the selected endpoint URI;
- the selection identifier for evidence correlation;
- the validated `TildenResolution` or the subset needed to establish the route;
- only those request constraints still needed for runtime policy or negotiation.

The complete private `TildenRequest` should remain caller-side unless a later profile explicitly authorizes disclosure.

## What Tilden does not prove

A successful Tilden selection MUST NOT be interpreted as proof that a call will succeed. Baudot retains responsibility for:

- SIP/WebRTC/RTT/media negotiation;
- runtime authentication and session security;
- codec and transport interoperability;
- fallback and transfer behavior;
- protocol error handling;
- session-level interoperability evidence.

Tilden proves only that, given the validated discovery result and the caller's selection policy, a particular endpoint was the deterministic candidate.

## Evidence correlation

Baudot should carry `selectionId` into its runtime evidence so a session attempt can be traced back to the exact routing decision without embedding the caller's full request.

Conceptually:

```text
TildenSelection(selectionId=sel-abc...)
        |
        v
Baudot session attempt
        |
        v
Baudot interoperability trace
        |
        v
WindAnvil / assurance bundle
```

## Reference CLI handoff

The current reference flow is:

```bash
tilden resolve ...  -o resolution.json
tilden request ...  -o request.json
tilden select resolution.json request.json -o selection.json
tilden explain selection.json
```

A future Baudot reference integration can consume `selection.json` directly, for example:

```text
baudot call --selection selection.json
```

That command is an intended integration shape, not yet a claim that Baudot implements this exact CLI surface.

Conversely, Tilden MUST NOT require Baudot-specific fields in its core objects. Implementations other than Baudot must be able to consume the same resolution and selection contracts.
