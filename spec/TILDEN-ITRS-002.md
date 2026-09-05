# TILDEN-ITRS-002 — DNS/ENUM Compatibility Profile

Status: Draft

## 1. Purpose

This profile defines a clean-room compatibility model for iTRS routing environments that expose telephone-number resolution through DNS/ENUM-style NAPTR and SRV processing.

It complements `TILDEN-ITRS-001`, which defines the general protected-authority adapter. `TILDEN-ITRS-002` describes one observed fielded resolution pattern and how a Tilden adapter can normalize that pattern without making DNS/ENUM part of the Tilden core protocol.

## 2. Prior-art observation

The public ACE Direct implementation demonstrates an iTRS routing chain in which a ten-digit telephone number is transformed into a reversed-digit ENUM-style name under an iTRS namespace, queried for NAPTR data, optionally followed through a CNAME-style forwarding step, resolved to an `E2U+sip` target, and then further resolved using ordinary DNS NAPTR and SRV records to obtain a SIP host and port.

This profile specifies the behavior independently. It does not incorporate ACE Direct source code.

## 3. Architectural rule

> Preserve the authoritative resolution chain; normalize only at the Tilden boundary.

```text
E.164 / NANP identifier
        |
        v
protected iTRS DNS adapter
        |
        +--> private iTRS NAPTR lookup
        |       |
        |       +--> optional alias / forwarding target
        |       +--> E2U+sip target
        |
        +--> public/private DNS NAPTR
        |
        +--> DNS SRV
        |
        v
resolved SIP host:port
        |
        v
Tilden route object
        |
        v
Baudot / SIP session establishment
```

Tilden MUST NOT require callers to understand ENUM, NAPTR, SRV, or the iTRS DNS namespace.

## 4. Telephone-number normalization

An adapter MUST normalize an input NANP identifier before constructing a DNS query name.

The adapter SHOULD accept canonical Tilden identifiers such as:

```text
tel:+12025550142
```

The protected iTRS adapter may then derive the administrator-specific lookup form required by the authoritative environment.

The derived DNS query name is an implementation detail and MUST NOT become the canonical Tilden identifier.

## 5. NAPTR resolution

Where the authoritative iTRS environment uses NAPTR records, the adapter SHALL interpret only record classes and services necessary to derive an authorized communications route.

The observed compatibility behavior includes:

1. query the iTRS telephone-number name for NAPTR-related routing information;
2. honor an authoritative alias/forwarding indirection when present;
3. otherwise select the applicable `E2U+sip` result;
4. apply NAPTR ordering/preference according to the authoritative DNS data; and
5. produce the resulting SIP-domain target as an intermediate route value.

An adapter MUST NOT infer a provider from stale local tables when the authoritative NAPTR result supplies a current route.

## 6. Alias and forwarding behavior

The compatibility profile allows the authoritative iTRS system to redirect resolution through an alias before a final `E2U+sip` result is obtained.

Tilden SHALL treat such indirection as part of authority resolution, not as a new user identity.

```text
number
  -> iTRS lookup name
  -> alias target, if any
  -> E2U+sip target
```

This is important for portability and forwarding-like behavior: the original telephone number remains the Tilden identity even when the authoritative routing path changes underneath it.

## 7. SIP service discovery

After an `E2U+sip` target is obtained, an implementation MAY follow DNS service discovery to determine the reachable SIP transport endpoint.

A compatible sequence may include:

```text
SIP domain
   -> NAPTR transport/service selection
   -> SRV lookup
   -> host + port
```

The adapter SHOULD preserve the distinction between:

- the logical SIP URI returned by iTRS resolution; and
- the network host/port selected through DNS service discovery.

The logical URI belongs in the Tilden route. Transport-resolution details may be retained as transient connection metadata for Baudot or another SIP consumer.

## 8. Route normalization

A successful compatibility lookup SHOULD produce a Tilden route similar to:

```json
{
  "uri": "sip:2025550142@example-vrs.invalid",
  "transport": "sip",
  "capabilities": ["sip", "video", "asl"],
  "authority": {
    "type": "fcc-itrs-directory",
    "profile": "tilden-itrs-002"
  },
  "provenance": {
    "method": "itrs-dns-enum",
    "freshness": "per-call"
  }
}
```

A Tilden implementation SHOULD avoid publishing resolved provider hostnames or ports when the logical routing URI is sufficient and disclosure is not required.

## 9. Simple verification vs. full routing

Fielded implementations may expose two useful behaviors:

- **verification** — determine whether an authoritative iTRS SIP route exists for a number; and
- **full resolution** — continue through DNS service discovery to obtain a network-reachable SIP destination.

Tilden SHOULD model these as separate operations or policy modes.

A public `resolve` request normally needs only the logical route. Full network service discovery is better performed within the protected adapter or by the downstream Baudot/SIP layer immediately before session establishment.

## 10. Retry and fallback

DNS resolution can fail transiently. Implementations MAY retry authoritative NAPTR or SRV lookups according to bounded policy.

A failure to obtain an SRV record MUST NOT automatically prove that the iTRS number is invalid.

Likewise, a failure of the protected iTRS DNS service MUST be distinguishable from an authoritative negative result.

Any fallback to a default SIP port, PSTN route, or other transport MUST be explicit policy and MUST NOT overwrite the authoritative iTRS identity state.

## 11. Provider mapping

Legacy implementations may map a resolved SIP host to a locally configured provider label.

Tilden SHOULD NOT require this mapping for routing correctness.

Provider labels may be useful for observability or policy, but the authoritative route URI is the primary result. A provider name MUST NOT become the durable owner of the telephone-number identity.

## 12. Security boundary

The private iTRS resolver address, private DNS path, credentials, network ACLs, and administrator-specific configuration remain inside the protected adapter.

```text
Tilden edge
   |
   | authenticated request
   v
protected adapter
   |
   | restricted DNS query
   v
iTRS authority
```

A public Worker MUST NOT become an unrestricted recursive or forwarding interface into the protected iTRS DNS environment.

## 13. Clean-room implementation rule

This specification was informed by observable behavior in the public ACE Direct repositories.

The Tilden implementation SHALL be independently written from this behavioral specification and applicable public standards/documentation. Source code from ACE Direct MUST NOT be copied into Tilden unless separate rights are established that permit that use.

This rule exists because the ACE Direct repository includes a MITRE rights notice that does not grant general unrestricted reuse.

## 14. Relationship to TILDEN-ITRS-001

`TILDEN-ITRS-001` defines *who may query and how the authority boundary is represented*.

`TILDEN-ITRS-002` defines *how a DNS/ENUM-style iTRS routing result can be derived and normalized*.

An implementation can support `TILDEN-ITRS-001` without supporting this compatibility profile if its authorized numbering interface uses another transport, such as a REST query service.

## 15. Relationship to Baudot

Tilden stops after producing an authoritative SIP route and any permitted connection metadata.

Baudot may then perform SIP signaling, transport negotiation, VRS interoperability, or other session-establishment behavior.

This keeps the boundary intact:

> Tilden resolves. Baudot connects.

## 16. References

- `TILDEN-ITRS-001`, TRS Numbering Directory Query Profile.
- `TILDEN-CORE-003`, Tilden Resolution Protocol.
- RFC 3403, Dynamic Delegation Discovery System (DDDS) Part Three: The Domain Name System (DNS) Database.
- RFC 3761, The E.164 to Uniform Resource Identifiers (URI) Dynamic Delegation Discovery System (DDDS) Application (ENUM).
- RFC 3263, Locating SIP Servers.
- MITRE ACE Direct public repositories, including the documented iTRS lookup integration and `asterisk/scripts/itrslookup.sh`, used as behavioral prior art only.
