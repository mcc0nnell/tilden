# Baudot handoff

Tilden returns a versioned `TildenResolution`. Baudot may consume that object as an input to session establishment.

The contract intentionally ends before signaling/media negotiation:

```text
TildenResolution
  |- canonical identity
  |- authoritative endpoint(s)
  |- asserted capabilities
  |- trust metadata
  `- expiry
        |
        v
Baudot policy gate
        |
        +-- reject: trust/local policy/conformance failure
        |
        `-- accept
              |
              v
        session negotiation
        SIP / WebRTC / RTT / video / other adapters
```

A successful Tilden resolution MUST NOT be interpreted as proof that a call will succeed. Baudot retains responsibility for protocol negotiation, runtime security, fallback, and interoperability evidence.

Conversely, Tilden MUST NOT require Baudot-specific fields in its core resolution object. Implementations other than Baudot must be able to consume the same object.
