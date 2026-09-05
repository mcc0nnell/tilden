# ACE Direct iTRS prior-art notes

ACE Direct is useful prior art for Tilden because its public implementation shows a working iTRS resolution path rather than only an abstract numbering model.

## What ACE Direct demonstrates

The relevant ACE Direct behavior includes:

- an explicit `itrs_mode` switch for validating VRS telephone numbers against iTRS rather than a local application database;
- a protected lookup script invoked by the application layer;
- normalization of NANP telephone numbers before resolution;
- construction of a reversed-digit ENUM-style lookup name in an iTRS namespace;
- private NAPTR lookup against a configured iTRS DNS server;
- support for an alias/forwarding indirection;
- extraction and priority handling of an `E2U+sip` result;
- optional continuation through ordinary DNS NAPTR and SRV discovery;
- derivation of a SIP host and port for session establishment; and
- optional mapping of the resolved host to a configured provider label.

The important architectural lesson for Tilden is that **iTRS resolution is already layered**:

```text
telephone number
    -> authoritative iTRS number resolution
    -> logical SIP URI
    -> DNS SIP service discovery
    -> SIP transport endpoint
```

Tilden should preserve those layers instead of collapsing them into a provider lookup.

## Tilden mapping

The clean Tilden mapping is:

```text
tel:+1...
    -> protected iTRS adapter
    -> authoritative iTRS route
    -> Tilden resolution object
    -> Baudot
    -> SIP service discovery / signaling as needed
```

This suggests two useful modes:

1. **route verification**: determine whether the number has an authoritative iTRS SIP route;
2. **connection resolution**: continue from the logical SIP route to a host/port immediately before establishing the session.

The first belongs naturally to Tilden. The second can stay at the Tilden/Baudot boundary or inside Baudot.

## Portability implication

ACE Direct's lookup behavior reinforces a core Tilden rule: provider identity should be derived from the current authoritative route, if it is needed at all. A locally configured provider label is an implementation convenience, not the durable owner of the telephone number.

This is why Tilden says:

> The number owns the route. The route does not own the number.

## Source-use boundary

The ACE Direct repository contains a MITRE rights notice associated with work produced for the U.S. Government and does not present a conventional permissive open-source grant for unrestricted reuse.

Accordingly, Tilden treats ACE Direct as **behavioral prior art and an interoperability reference**, not as a source-code donor.

Tilden implementations should be written independently from Tilden specifications, public standards, and independently established interface requirements. No ACE Direct source code should be copied into Tilden absent separate rights permitting that reuse.

## Public references

- https://github.com/mitre-ace-direct/ace-direct
- https://github.com/mitre-ace-direct/asterisk/blob/master/scripts/itrslookup.sh
- `TILDEN-ITRS-001`
- `TILDEN-ITRS-002`
