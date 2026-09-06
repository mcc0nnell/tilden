# ACE Direct iTRS resolution donor provenance

Status: **research donor, non-normative**  
Tilden target: `TILDEN-CORE-001` discovery and legacy-compatibility research

## Why preserve this

ACE Direct contains a concrete production-era model for taking a video-relay telephone number and resolving it toward a provider SIP endpoint. Tilden should preserve the useful behavioral lessons without copying the implementation or treating its shell parsing, retry choices, DNS trust assumptions, or portal coupling as a modern protocol definition.

The donor is valuable because it demonstrates a real separation that Tilden now makes explicit:

```text
human-reachable number
  -> numbering/discovery namespace
  -> provider/service target
  -> routable SIP host/port
  -> calling runtime
```

That is a discovery contract. It is not a media-conformance verdict.

## Pinned donor surfaces

### ACE Direct Asterisk fork

```text
repository: mitre-ace-direct/asterisk
commit:     cbfc11e7660ed9d64c98d72336b3de3ea7b3aa33
file:       scripts/itrslookup.sh
blob:       40f3be73d9fc85e39d613183715d1a46d4043a61
```

The script exposes two modes:

- `simple`: determine whether the number resolves to an `E2U+sip` result in the iTRS discovery path and return the discovered value to the caller;
- `full`: continue from iTRS discovery through ordinary DNS NAPTR and SRV resolution, derive a host and port, and optionally map known provider hosts to configured endpoint labels.

### ACE Direct consumer portal

```text
repository: mitre-ace-direct/ace-direct
commit family: v61-prod
file:       mserver/routes/userver.js
blob:       6dc17dfd6386191c409c66aac7e4f5adc410129c
```

The `/vrsverify` route accepts a ten-digit video-phone number. When iTRS mode is enabled it invokes `itrslookup.sh` in `simple` mode and treats a non-empty returned `sipuri` field as successful iTRS verification. When iTRS mode is disabled the same route falls back to the application's local database.

The top-level ACE Direct README separately instructs operators to copy `asterisk/scripts/itrslookup.sh` into the ACE Direct deployment and configure it for desired providers. That establishes the script as an intentional cross-repository integration surface rather than an unrelated utility.

## Observed donor state machine

The historical implementation can be reduced to these observable stages:

```text
input number
  -> NANP-oriented normalization
  -> reversed-digit iTRS ENUM-family query name
  -> iTRS NAPTR lookup
       -> optional alias/CNAME hop
       -> E2U+sip selection
  -> SIMPLE: return discovered SIP/provider value
  -> FULL:
       -> ordinary DNS NAPTR lookup for SIP transport
       -> bounded retry
       -> fallback attempt using port 5060 when transport NAPTR is absent
       -> SRV lookup
       -> bounded retry
       -> host + port extraction
       -> optional configured-provider classification
       -> return route
```

The script derives the iTRS query name from reversed number digits and the `itrs.us` namespace, with a `.1` suffix in the constructed name. It also contains an alias/CNAME branch before selecting an `E2U+sip` NAPTR result.

The full path performs separate NAPTR and SRV stages and retries each bounded stage up to four attempts. The implementation includes a port-5060 fallback when the transport-resolution stage cannot produce a usable result.

## What Tilden should learn from it

### Preserve these concepts

1. **Identity and route are different facts.** A telephone number is the input identity; a SIP host/port is a discovered route.
2. **Resolution is multi-stage.** A successful first namespace lookup may delegate to another DNS name before a routable endpoint exists.
3. **Provider portability is possible.** The number can remain stable while the authoritative provider target changes.
4. **Discovery success is not session success.** ACE's lookup ends before SIP/media interoperability is established; that boundary belongs between Tilden and a runtime such as Baudot.
5. **Fallbacks and retries are observable policy.** They should be explicit in evidence rather than hidden inside shell control flow.
6. **Legacy integration surfaces matter.** A modern resolver should be able to front or emulate a legacy discovery source without forcing consumers to reproduce its implementation details.

### Do not promote these implementation details to Tilden requirements

- shell command parsing with `dig`, `host`, `grep`, `awk`, `cut`, and positional stdout parsing;
- provider configuration as hard-coded shell variables;
- ten-digit NANP assumptions as a global identifier rule;
- unauthenticated DNS results as sufficient modern trust evidence;
- implicit interpretation of empty output as a portable failure taxonomy;
- the literal retry count of four;
- the literal port-5060 fallback;
- portal behavior that conflates "a discovery value exists" with a stronger statement about service usability.

These are historical implementation facts and scenario donors, not normative Tilden behavior.

## Mapping to TILDEN-CORE-001

| ACE/iTRS donor concept | Tilden concept |
| --- | --- |
| video-phone number | input identifier / `canonicalIdentity` |
| iTRS namespace | discovery profile / authority namespace |
| CNAME-style indirection | explicit authority or route delegation |
| `E2U+sip` NAPTR result | intermediate service discovery result |
| NAPTR/SRV host and port | `endpoints[]` |
| configured provider match | endpoint/authority metadata, not local shell state |
| simple lookup success | discovery success only |
| full lookup failure/retry | explicit failure/evidence state |
| local DB fallback | resolver policy / alternate authority source |
| SIP call after lookup | consumer responsibility, outside Tilden core |

The current Draft 0.1 intentionally leaves discovery transport open. The ACE donor is therefore evidence for keeping an ENUM-family/DNS profile possible; it is not evidence that Tilden Core must require DNS or `itrs.us`.

## Mocking rule

Tilden's ACE-derived mocks MUST model the state transitions and evidence facts above. They MUST NOT execute the historical script, query production iTRS infrastructure, copy provider configuration, or make claims about current provider routing.

Use reserved example names and addresses. A mock result derived from this donor is evidence that Tilden can represent a legacy resolution flow, not evidence that a real telephone number currently belongs to a VRS provider.

## Provenance boundary

This document is a behavioral reading of public ACE Direct source. It does not claim that every production iTRS deployment behaved identically, that the historical DNS data is still current, or that the donor implementation is conformant to any present-day Tilden profile.
