# TILDEN-AUTH-003: Resolver Authority and Bootstrap

**Status:** Draft 0.1  
**Category:** Core Profile  
**Updated:** 2026-09-05

## 1. Abstract

Tilden resolution is useful only if a client can determine which resolver is authorized to speak for a communications identity.

This specification defines the authority and bootstrap model that binds a Tilden subject, initially an E.164 number, to an authoritative resolver and to the keys that may sign Tilden objects for that subject.

The critical distinction is:

```text
HTTPS origin authority != Tilden subject authority
```

A valid TLS certificate can prove that a client is connected to `resolver.example.net`. It does not, by itself, prove that `resolver.example.net` is authorized to publish routes for `+12025550123`.

TILDEN-AUTH-003 fills that gap.

## 2. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as normative requirements.

## 3. Scope

This specification defines:

1. the Tilden authority delegation object;
2. exact-number and number-prefix delegation;
3. resolver bootstrap behavior;
4. trust-anchor policy;
5. DNSSEC/ENUM integration;
6. a signed registry bootstrap profile;
7. key rotation, transfer, revocation, and expiry;
8. conflict handling and failure behavior;
9. security requirements for authority discovery.

This specification does not define:

- allocation of E.164 numbers;
- number-porting policy;
- carrier subscriber authentication;
- SIP, IMS, VRS, or media-session authentication;
- a universal global Tilden root;
- proof that a human owns or controls a telephone number;
- the signature profile for ordinary Tilden Resolution Objects.

## 4. Authority model

Tilden separates four forms of authority:

```text
numbering authority
      |
      v
Tilden delegation authority
      |
      v
Tilden resolver authority
      |
      v
endpoint/session authority
```

These authorities MAY be operated by different organizations.

A client MUST NOT infer one authority from another unless an applicable Tilden profile explicitly defines that relationship.

### 4.1 Numbering authority

A numbering authority allocates or delegates use of an E.164 number or number block under applicable telecommunications rules.

Tilden does not replace this function.

### 4.2 Tilden delegation authority

A Tilden delegation authority is trusted, under client policy, to bind a Tilden subject or subject prefix to one or more Tilden resolver authorities.

### 4.3 Tilden resolver authority

A Tilden resolver authority is authorized to publish Tilden Resolution Objects for the delegated subject scope.

### 4.4 Endpoint authority

An endpoint remains responsible for authenticating its own session or application protocol.

A valid Tilden delegation and a valid Tilden Resolution Object do not automatically authenticate a SIP peer, VRS provider, carrier session, messaging service, or proprietary platform endpoint.

## 5. Authority Delegation Object

A Tilden Authority Delegation Object binds a subject scope to an authoritative resolver.

Example payload:

```json
{
  "tilden_version": "1",
  "object_type": "authority-delegation",
  "delegation_id": "tdel_01J7TILDEN000000000000001",
  "serial": 42,
  "scope": {
    "type": "e164",
    "prefix": "+12025550123"
  },
  "resolver": "https://resolver.example.net",
  "signing_keys": [
    {
      "kid": "2026-09-a",
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "11qYAYdk9J..."
    }
  ],
  "valid_from": "2026-09-05T21:00:00Z",
  "valid_until": "2026-12-05T21:00:00Z"
}
```

## 6. Required delegation fields

A delegation object MUST contain:

- `tilden_version` — object version;
- `object_type` — MUST equal `authority-delegation`;
- `delegation_id` — stable identifier for the delegation lineage;
- `serial` — monotonically increasing integer within that lineage;
- `scope` — identity or identity range covered by the delegation;
- `resolver` — HTTPS origin of the authorized Tilden resolver;
- `signing_keys` — zero or more public keys authorized for Tilden object signatures;
- `valid_from` — earliest time at which the delegation is valid;
- `valid_until` — latest time at which the delegation is valid.

A delegation MAY contain:

- `previous` — identifier or digest of the prior delegation;
- `successor` — expected successor delegation identifier;
- `policy` — non-secret constraints on resolver behavior;
- `metadata` — extension data.

Unknown fields MUST be ignored unless a future specification marks them critical.

## 7. Scope

### 7.1 Exact E.164 subject

An exact-number delegation uses the complete canonical E.164 number:

```json
{
  "type": "e164",
  "prefix": "+12025550123"
}
```

### 7.2 E.164 prefix

A delegation MAY cover a valid E.164 number prefix:

```json
{
  "type": "e164",
  "prefix": "+1202555"
}
```

Prefix delegation permits a provider, carrier, numbering administrator, enterprise, or federation operator to delegate a block without publishing one bootstrap record per number.

A prefix delegation MUST NOT be interpreted as allocation of the underlying numbers.

### 7.3 Longest-prefix rule

When multiple valid delegations from the same trusted delegation system match a subject, the delegation with the longest matching canonical prefix MUST win.

Example:

```text
+1202           -> resolver A
+1202555        -> resolver B
+12025550123    -> resolver C
```

For `+12025550123`, resolver C is authoritative.

This permits broad delegation with narrow overrides.

## 8. Bootstrap algorithm

A client resolving `tel:+12025550123` performs the following steps:

1. canonicalize the subject according to TILDEN-CORE-001;
2. select one or more bootstrap methods permitted by local trust policy;
3. obtain candidate authority delegations;
4. authenticate the delegation source;
5. validate delegation freshness and scope;
6. apply longest-prefix and conflict rules;
7. determine the authoritative resolver origin;
8. establish authenticated HTTPS to that origin;
9. retrieve the Tilden Resolution Object;
10. validate that the resolution object's `authority` matches the delegated authority;
11. when object signing is used, validate the object against a key authorized by the delegation;
12. continue TILDEN-CORE-001 resolution semantics.

A client MUST fail closed for Tilden resolution when it cannot establish subject authority.

Failure of Tilden authority discovery MUST NOT be treated as proof that the underlying telephone number is invalid or unreachable through non-Tilden systems.

## 9. Bootstrap methods

Tilden intentionally supports more than one authority-discovery mechanism.

A deployment MAY support:

- DNSSEC/ENUM delegation;
- a signed Tilden bootstrap registry;
- numbering-authority integration;
- bilateral federation configuration;
- enterprise or private trust domains;
- future standardized mechanisms.

A client MUST have an explicit trust policy for every bootstrap method it accepts.

Discovery without an authenticated trust path MUST NOT establish Tilden authority.

## 10. DNSSEC/ENUM profile

### 10.1 Relationship to ENUM

RFC 6116 defines ENUM as a mechanism for mapping E.164 telephone numbers through DNS into URI-based services.

Tilden MAY use ENUM as a standards-aligned bootstrap mechanism when the relevant E.164 namespace is delegated and operational for that deployment.

Tilden implementations MUST NOT assume that public ENUM delegation exists for every E.164 number or country code.

### 10.2 DNSSEC requirement

A DNS bootstrap result MUST NOT establish Tilden subject authority unless the client validates an authenticated DNSSEC chain to a locally trusted DNSSEC trust anchor.

Unsigned DNS MAY be used for discovery hints but MUST NOT, by itself, authorize a resolver to speak for a Tilden subject.

### 10.3 Enumservice registration

A future interoperable public ENUM profile SHOULD define and register an appropriate Tilden Enumservice according to the applicable IANA and IETF procedures.

Experimental implementations MUST NOT squat on an unregistered public Enumservice identifier in production `e164.arpa` zones.

Private test zones MAY use locally agreed experimental records.

### 10.4 Output

The authenticated ENUM result SHOULD ultimately identify either:

1. an HTTPS Tilden resolver origin; or
2. a signed Tilden Authority Delegation Object.

DNS records SHOULD remain small and SHOULD point to richer HTTPS metadata rather than embedding large capability documents in DNS.

## 11. Signed registry bootstrap profile

The first deployable Tilden reference profile uses one or more configured bootstrap registries.

A registry MAY expose:

```text
GET /.well-known/tilden/v1/authority?subject=tel%3A%2B12025550123
```

The response SHOULD use:

```text
Content-Type: application/tilden-authority+jose
```

The payload MUST be a Tilden Authority Delegation Object protected by JSON Web Signature (JWS).

The signer MUST chain to, or be directly identified by, a trust anchor configured by the client.

Authenticated TLS is REQUIRED for the registry transport even when the returned delegation is independently signed.

The well-known URI convention is consistent with RFC 8615; a production registration SHOULD use an appropriately registered well-known name rather than relying indefinitely on an experimental path.

## 12. Registry trust anchors

A Tilden client MAY trust one or more bootstrap registries.

Trust anchors MAY be distributed through:

- operating-system or application configuration;
- enterprise policy;
- federation configuration;
- standards-based numbering infrastructure;
- another authenticated provisioning channel.

Tilden does not require one universal bootstrap registry.

A client MUST NOT silently add a new delegation trust anchor because an untrusted network response instructed it to do so.

## 13. JWS envelope

For the signed registry profile, the Authority Delegation Object MUST be carried as the payload of a JWS using an asymmetric digital signature algorithm.

The protected JWS header MUST contain:

- `alg` — approved asymmetric signature algorithm;
- `kid` — identifier of the delegation-signing key;
- `typ` — `tilden-authority+jwt` or a future registered equivalent.

The JWS payload bytes are authoritative. A verifier MUST verify the JWS before reparsing or reserializing the JSON payload.

The `none` algorithm and symmetric MAC algorithms MUST NOT be used for federation authority delegations.

A future cryptographic profile MAY narrow the allowed algorithm set.

## 14. Resolver binding

The `resolver` field names the HTTPS origin authorized for the delegation scope.

Example:

```text
https://resolver.example.net
```

The field MUST NOT contain userinfo, a fragment, or an untrusted redirect target.

Clients MUST authenticate the HTTPS origin according to normal TLS/Web PKI rules.

Clients MUST NOT follow a cross-origin redirect during authoritative resolution unless the target origin is also explicitly authorized by a current delegation.

This prevents an authorized resolver origin from silently transferring subject authority through HTTP redirection alone.

## 15. Resolution-object binding

A Tilden Resolution Object returned for a delegated subject MUST identify an `authority` consistent with the active Authority Delegation Object.

A client MUST reject a resolution object when:

- its subject is outside the active delegation scope;
- its authority does not match the delegated resolver;
- it was issued outside the delegation validity period;
- it expires after a policy-imposed maximum validity interval;
- a required signature cannot be validated against a currently authorized signing key.

TLS authenticates the live resolver connection. Object signatures, when present, permit integrity to survive caching, federation intermediaries, and offline verification.

## 16. Key binding

The `signing_keys` array identifies public keys that MAY sign Tilden objects for the delegation scope.

A key entry MUST contain:

- `kid` — key identifier;
- sufficient public-key material to verify signatures.

Private key material MUST NOT appear in a delegation object.

A resolver MAY publish no signing keys when operating a TLS-only profile, but clients or federation policies MAY require signed resolution objects.

## 17. Key rotation

A resolver SHOULD rotate signing keys without changing the Tilden subject.

During an overlap window, a delegation MAY authorize both the outgoing and incoming keys.

Example:

```text
serial 41: key A
serial 42: key A + key B
serial 43: key B
```

A client MUST prefer the highest valid serial for a delegation lineage.

A client MUST NOT treat a lower serial learned later as a rollback unless an explicit disaster-recovery policy allows it.

## 18. Resolver transfer and portability

Changing providers MUST NOT require changing the Tilden subject.

A resolver transfer SHOULD produce a new delegation with:

- the same subject scope or a valid subdivision of it;
- an incremented serial;
- the new resolver origin;
- new signing keys as appropriate;
- lineage information linking the prior delegation when available.

Conceptually:

```text
+12025550123
      |
      +-- serial 41 -> resolver-a.example
      |
      +-- serial 42 -> resolver-b.example
```

The newer valid delegation wins.

The old resolver MUST NOT remain authoritative after the transfer becomes effective unless the new delegation explicitly retains it.

## 19. Number reassignment

Telephone numbers can be disconnected and reassigned.

A Tilden deployment MUST treat number reassignment as a security-sensitive identity lifecycle event.

When control of an E.164 number ends:

1. subject-specific delegations SHOULD be revoked or allowed to expire promptly;
2. resolver signing keys scoped only to that subject SHOULD cease to be authoritative;
3. caches MUST respect revocation and expiry policy;
4. stale accessibility routes MUST NOT survive indefinitely into a new subscriber's tenure.

Long-lived permanent bindings are NOT RECOMMENDED for reassignment-prone numbering resources.

## 20. Revocation

A delegation authority MUST support a mechanism to invalidate a delegation before `valid_until` when necessary.

A revocation record MUST identify at least:

- the affected `delegation_id`;
- the minimum invalid serial or exact serial range;
- the revocation effective time.

Clients SHOULD obtain revocation state whenever bootstrap freshness policy requires it.

Short delegation lifetimes MAY reduce but do not eliminate the need for revocation.

## 21. Caching

Authority delegations MAY be cached until the earliest of:

- `valid_until`;
- an explicit cache-control limit;
- a verified revocation;
- a local maximum bootstrap TTL.

Clients SHOULD use conservative cache lifetimes for exact-number delegations because telephone-number control can change.

A stale delegation MUST NOT be used to establish a new authoritative Tilden route unless explicit offline policy permits degraded behavior.

## 22. Conflict handling

### 22.1 Same trust system

Within one authenticated delegation system:

1. longest matching scope wins;
2. within the same scope and lineage, highest valid serial wins;
3. revoked delegations lose;
4. expired or not-yet-valid delegations lose.

### 22.2 Different trust systems

Two independently trusted bootstrap systems MAY disagree.

A client MUST apply explicit local policy and MUST NOT silently merge the conflicting delegations.

Possible policies include:

- prefer numbering-authority-backed delegation;
- prefer DNSSEC/ENUM;
- prefer an enterprise trust domain;
- require agreement between two systems;
- fail closed on disagreement.

The selected policy SHOULD be auditable.

## 23. Enrollment evidence

A bootstrap operator MAY use evidence such as:

- carrier or numbering-provider APIs;
- authenticated porting records;
- enterprise numbering records;
- contract or account validation;
- temporary possession challenges;
- regulator or numbering-administrator data.

However, temporary receipt of an SMS or voice OTP SHOULD NOT be treated as sufficient long-term cryptographic authority by itself.

SIM swap, forwarding, recycled numbers, and compromised carrier accounts make possession challenges useful enrollment signals but poor permanent trust anchors.

Enrollment evidence SHOULD remain private unless disclosure is necessary and lawful.

## 24. Transparency

A bootstrap registry SHOULD make authority changes auditable.

Deployments MAY use:

- append-only transparency logs;
- signed checkpoints;
- public change histories;
- independent monitors;
- externally auditable delegation serials.

Transparency is especially valuable for detecting:

- unauthorized resolver transfers;
- split-view attacks;
- rollback attacks;
- unexpected high-level prefix delegation.

Transparency does not replace authentication or authorization.

## 25. Threat model

Implementations MUST consider at least:

### 25.1 Rogue resolver

An attacker operates a valid HTTPS service and claims authority for numbers it does not control.

**Mitigation:** authenticated delegation separate from TLS origin authentication.

### 25.2 DNS spoofing

An attacker injects false DNS bootstrap responses.

**Mitigation:** DNSSEC validation for DNS-based authority discovery.

### 25.3 Stale delegation

A former provider continues serving valid-looking routes after a transfer.

**Mitigation:** bounded validity, monotonic serials, revocation, and key rotation.

### 25.4 SIM swap or possession theft

An attacker temporarily receives messages or calls for the number.

**Mitigation:** possession challenges are not permanent trust anchors; sensitive transfers require stronger evidence and policy.

### 25.5 Registry compromise

A trusted bootstrap registry is compromised.

**Mitigation:** short-lived delegations, offline or threshold-protected signing keys, transparency, independent monitoring, and support for multiple trust systems.

### 25.6 Split view

Different clients receive inconsistent delegation histories.

**Mitigation:** transparency logs, signed checkpoints, serial continuity, and monitor comparison.

### 25.7 Redirect capture

An authorized resolver redirects clients to an unauthorized origin.

**Mitigation:** cross-origin redirects do not transfer Tilden subject authority.

## 26. Privacy

Bootstrap responses SHOULD reveal only information needed to establish authority.

They MUST NOT expose:

- IMSI;
- ICCID;
- eSIM activation secrets;
- carrier account credentials;
- private subscriber identity documents;
- private enrollment evidence;
- device identifiers;
- platform account identifiers.

A prefix delegation SHOULD be preferred over publishing subscriber-by-subscriber metadata when equivalent authority can be expressed safely at the block level.

## 27. Failure states

Authority discovery SHOULD distinguish at least:

- `authority-not-found` — no trusted delegation exists;
- `authority-conflict` — trusted bootstrap methods disagree;
- `authority-expired` — only expired delegations were found;
- `authority-revoked` — current delegation has been revoked;
- `authority-invalid` — signature, scope, or syntax validation failed;
- `authority-unavailable` — trusted bootstrap infrastructure is temporarily unreachable.

Clients MUST NOT downgrade an authority-validation failure into acceptance of an unauthenticated resolver.

## 28. Reference bootstrap flow

```text
User dials / selects
+1 202 555 0123
        |
        v
Canonical subject
 tel:+12025550123
        |
        v
Bootstrap policy
   /         \
  /           \
DNSSEC/ENUM   Signed registry
  \           /
   \         /
 Authenticated delegation
        |
        v
https://resolver.example.net
        |
        v
Tilden Resolution Object
        |
        v
SIP / RTT / VRS / Baudot / PSTN / other endpoint
```

## 29. Reference registry example

A development client configured to trust `bootstrap.tilden.example` MAY perform:

```http
GET /.well-known/tilden/v1/authority?subject=tel%3A%2B12025550123 HTTP/1.1
Host: bootstrap.tilden.example
Accept: application/tilden-authority+jose
```

After validating the returned signed delegation, it MAY contact:

```http
GET /.well-known/tilden/v1/resolve?subject=tel%3A%2B12025550123 HTTP/1.1
Host: resolver.example.net
Accept: application/tilden+json
```

The second request is authoritative only because the first authenticated delegation authorized `resolver.example.net` for that subject.

## 30. Relationship to TILDEN-CORE-001

TILDEN-CORE-001 defines:

```text
identity -> resolution -> endpoint -> session
```

This specification expands the second step:

```text
identity
   |
   v
authenticated authority bootstrap
   |
   v
authorized resolver
   |
   v
resolution
```

A Tilden client claiming conformance to authenticated public federation MUST implement an authority-bootstrap policy consistent with this specification.

## 31. Relationship to TILDEN-ESIM-002

An active eSIM or carrier subscription MAY be evidence used during enrollment or lifecycle management, but it does not itself become the Tilden bootstrap protocol.

Carrier identity and Tilden resolver authority remain separate trust domains.

This preserves the Tilden invariant:

> **NUMBER != NETWORK**

## 32. Design invariant

The central authority invariant is:

> **ORIGIN != SUBJECT AUTHORITY**

A server is not entitled to speak for a telephone number merely because it has HTTPS, DNS, carrier connectivity, or a working endpoint.

Authority must be explicitly delegated through an authenticated trust path.

That allows Tilden to remain federated without becoming unauthenticated.