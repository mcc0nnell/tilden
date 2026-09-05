# TILDEN-CORE-001: Identity, Discovery, and Capability Resolution

**Status:** Draft 0.1  
**Category:** Core  
**Updated:** 2026-09-05

## 1. Abstract

Tilden defines a neutral resolution layer for real-time communications. A Tilden identifier names a communications identity; resolution returns the currently authorized ways to reach that identity.

The central invariant is:

> **NUMBER != NETWORK**

An E.164 number can remain the human-facing rendezvous identifier while calls and messages are completed over different transports, providers, accessibility modalities, or proprietary platforms.

Tilden does not require a single calling stack. It describes what endpoints exist, what they can do, and which authority asserted them.

## 2. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as normative requirements.

## 3. Goals

Tilden is designed to provide:

1. stable human-reachable identifiers;
2. provider-independent endpoint discovery;
3. explicit accessibility capability metadata;
4. coexistence with PSTN, SIP, RTT, VRS, messaging, and native platform services;
5. bounded, auditable authority over published routes;
6. safe federation without requiring every participant to trust every other participant directly.

## 4. Non-goals

Tilden is not:

- a media transport;
- a SIP replacement;
- an IMS implementation;
- a relay service;
- a FaceTime or iMessage emulator;
- a universal identity provider;
- a mechanism for bypassing carrier or platform authorization.

## 5. Identifier model

### 5.1 Canonical telephone identifier

The initial Tilden profile uses E.164 telephone numbers as canonical public identifiers.

A resolver MUST canonicalize a telephone identifier to the form:

```text
+<country-code><national-number>
```

Example:

```text
+12025550123
```

Formatting characters, spaces, parentheses, and local dialing prefixes MUST NOT be retained in the canonical identifier.

### 5.2 Future identifiers

Future profiles MAY define non-E.164 identifiers. Implementations MUST NOT assume that every future Tilden subject is a telephone number.

## 6. Resolution object

A successful resolution returns a Tilden Resolution Object.

Example:

```json
{
  "tilden_version": "1",
  "subject": "tel:+12025550123",
  "issued_at": "2026-09-05T21:00:00Z",
  "expires_at": "2026-09-05T21:15:00Z",
  "authority": "https://resolver.example.net",
  "capabilities": [
    {
      "type": "sip",
      "uri": "sip:+12025550123@edge.example.net;user=phone",
      "priority": 20,
      "media": ["video", "audio", "rtt"],
      "features": ["asl", "t140"]
    },
    {
      "type": "vrs",
      "uri": "https://vrs.example.net/call/+12025550123",
      "priority": 30,
      "media": ["video"],
      "features": ["asl", "relay"]
    },
    {
      "type": "pstn",
      "uri": "tel:+12025550123",
      "priority": 100,
      "media": ["audio"]
    }
  ]
}
```

## 7. Required fields

A resolution object MUST contain:

- `tilden_version` — protocol object version;
- `subject` — canonical identity being resolved;
- `issued_at` — issuance time;
- `expires_at` — latest time at which the object may be relied upon;
- `authority` — identifier for the asserting resolver authority;
- `capabilities` — zero or more authorized communication endpoints.

A resolver MUST NOT return a capability that it is not authorized to assert for the subject.

## 8. Capability records

Each capability record MUST contain:

- `type` — endpoint or service class;
- `uri` — routable endpoint identifier;
- `priority` — relative routing preference, where lower values are preferred.

A capability record MAY include:

- `media` — supported media classes;
- `features` — supported accessibility or service features;
- `auth` — authentication requirements;
- `expires_at` — endpoint-specific expiration;
- `provider` — service provider identifier;
- `metadata` — extension data.

Unknown capability fields MUST be ignored unless an extension specification declares them critical.

## 9. Initial capability types

The initial registry reserves the following strings:

| Type | Meaning |
| --- | --- |
| `pstn` | conventional telephone-network reachability |
| `sip` | SIP endpoint |
| `rtt` | real-time text capable endpoint |
| `vrs` | video relay service endpoint |
| `video` | direct video endpoint |
| `message` | messaging endpoint |
| `baudot` | Baudot federation endpoint |
| `carrier-esim` | carrier-backed eSIM identity binding |

Capability type does not imply media. Implementations SHOULD inspect both `type` and `media`.

## 10. Initial media values

The initial media registry defines:

- `audio`
- `video`
- `text`
- `rtt`

## 11. Initial accessibility feature values

The initial feature registry defines:

- `asl` — American Sign Language video communication;
- `t140` — ITU-T T.140 real-time text;
- `captions` — real-time captions available;
- `relay` — communication traverses a relay service;
- `direct` — direct communication endpoint;
- `speech-to-text` — speech transcription available;
- `text-to-speech` — text-to-speech available.

These values describe capability, not user disability or identity. Public resolution objects SHOULD expose only information necessary to complete communication.

## 12. Resolution semantics

A client resolving a Tilden subject:

1. canonicalizes the identifier;
2. determines an authoritative Tilden resolver;
3. retrieves a current resolution object;
4. validates authority, freshness, and integrity;
5. filters capabilities against the caller and callee requirements;
6. selects the best acceptable endpoint;
7. hands the selected endpoint to the corresponding transport or application.

Tilden resolution ends at step 6. Session establishment belongs to the selected communications system.

## 13. Reference HTTPS profile

The first reference transport is HTTPS.

A resolver MAY expose:

```text
GET /.well-known/tilden/v1/resolve?subject=tel%3A%2B12025550123
```

A successful response SHOULD use:

```text
Content-Type: application/tilden+json
```

The response body is a Tilden Resolution Object.

HTTPS is an implementation profile, not the identity model. Future profiles MAY use ENUM/DNS, signed directories, carrier APIs, decentralized registries, or other discovery transports.

## 14. Caching

Clients MAY cache resolution objects until `expires_at`.

Resolvers SHOULD use short-lived objects for rapidly changing routes.

A client MUST NOT use an expired object for a new session unless an explicit offline policy permits stale resolution and clearly treats it as degraded behavior.

## 15. Authority and integrity

A client MUST establish that the resolver is authorized to speak for the subject before relying on its routes.

The HTTPS reference profile MUST use authenticated TLS.

A future signing profile SHOULD define portable signed resolution objects so that integrity can survive caching, federation, and intermediary transport.

Tilden authority MUST remain distinct from endpoint authentication. A valid resolution object says where a client may attempt communication; it does not automatically authenticate the remote application session.

## 16. Privacy

Resolvers MUST minimize published metadata.

Public resolution data MUST NOT expose carrier credentials, IMSI, ICCID, eSIM activation secrets, Apple Account identifiers, private device identifiers, or equivalent subscriber secrets.

Accessibility capability metadata SHOULD describe the endpoint rather than infer or disclose sensitive characteristics of the user.

## 17. Failure behavior

Resolvers SHOULD distinguish at least:

- `not-found` — no Tilden subject is known;
- `no-capability` — subject exists but no requested capability is available;
- `temporarily-unavailable` — authoritative resolution cannot currently complete;
- `not-authoritative` — resolver cannot assert routes for the subject;
- `invalid-subject` — identifier cannot be canonicalized or is unsupported.

A failure to resolve Tilden MUST NOT be treated as proof that the underlying telephone number or external platform identity does not exist.

## 18. Federation

Federation is based on authoritative resolution, not universal shared infrastructure.

Different providers MAY operate independent resolvers. A client MAY learn authority through a bootstrap registry, numbering authority integration, DNS/ENUM profile, bilateral trust, or another future standardized mechanism.

The bootstrap mechanism is intentionally separated from the resolution object so it can evolve without changing endpoint semantics.

## 19. Relationship to Baudot

Baudot MAY consume Tilden Resolution Objects to discover accessible real-time communications endpoints.

Tilden MUST remain usable without Baudot, and Baudot MUST NOT be required to operate a Tilden authority.

## 20. Design invariant

A conforming implementation MUST preserve this distinction:

```text
identity -> resolution -> endpoint -> session
```

It MUST NOT collapse identity into a single provider or transport.

The intended user experience is simple:

> **One number. Every modality.**
