# TILDEN-SIGN-004: Signed Resolution Objects

**Status:** Draft 0.1  
**Category:** Core Profile  
**Updated:** 2026-09-05

## 1. Abstract

Tilden Resolution Objects may be cached, replicated, relayed through federation infrastructure, or verified after the HTTPS transaction that originally carried them has ended. TLS alone cannot preserve integrity or subject authority across those boundaries.

This specification defines a signed representation of the Tilden Resolution Object using JSON Web Signature (JWS). The signature key is not discovered from the signed object. It MUST already be authorized for the subject by an active Tilden Authority Delegation Object under TILDEN-AUTH-003.

The trust chain is:

```text
subject
  -> authenticated bootstrap
  -> active authority delegation
  -> authorized signing key
  -> signed resolution object
  -> endpoint set
```

The critical invariant is:

> **A valid signature is not sufficient; the signing key MUST also be currently authorized for the subject.**

## 2. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as normative requirements.

## 3. Scope

This specification defines:

1. the signed wire representation of a Tilden Resolution Object;
2. required JOSE protected headers;
3. the initial signing algorithm profile;
4. binding to TILDEN-AUTH-003 signing keys;
5. verification order;
6. freshness, replay, rotation, transfer, and revocation behavior;
7. transport and caching semantics;
8. failure behavior and security requirements.

This specification does not define:

- bootstrap trust anchors;
- enrollment evidence for telephone-number authority;
- endpoint or media-session authentication;
- end-to-end encryption for a selected communications session;
- private-key custody mechanisms;
- a replacement for TLS.

## 4. Relationship to other Tilden specifications

TILDEN-CORE-001 defines the unsigned Tilden Resolution Object.

TILDEN-AUTH-003 defines which resolver and public signing keys are authorized for a subject.

TILDEN-SIGN-004 defines how an authorized key signs a Tilden Resolution Object and how a client verifies that signature.

A signature MUST NOT create authority that is absent from TILDEN-AUTH-003.

## 5. Wire representation

The initial signed profile uses the **Flattened JWS JSON Serialization** defined by RFC 7515.

A signed resolution response has exactly these top-level members:

```json
{
  "payload": "<base64url-encoded Tilden Resolution Object>",
  "protected": "<base64url-encoded protected JOSE header>",
  "signature": "<base64url-encoded signature>"
}
```

The JWS payload is the UTF-8 byte serialization of the ordinary Tilden Resolution Object defined by TILDEN-CORE-001.

The payload bytes covered by JWS are authoritative. A verifier MUST verify the JWS signing input before relying on parsed payload fields.

This profile does not require JSON canonicalization because JWS signs the exact payload octets. Intermediaries MUST NOT decode, reserialize, and replace the payload while retaining the original signature.

## 6. Media type

A signed resolution response SHOULD use:

```text
Content-Type: application/tilden-resolution+jws
```

Until a media type is formally registered, implementations MAY use this value as an experimental profile identifier.

The protected JWS `cty` header MUST identify the payload as:

```text
application/tilden+json
```

## 7. Protected JOSE header

The protected JOSE header MUST contain:

- `alg` — the approved signature algorithm;
- `kid` — identifier of the signing key from the active Authority Delegation Object;
- `typ` — `tilden-resolution+jws`;
- `cty` — `application/tilden+json`.

Example:

```json
{
  "alg": "Ed25519",
  "kid": "2026-09-a",
  "typ": "tilden-resolution+jws",
  "cty": "application/tilden+json"
}
```

All security-relevant JOSE parameters MUST be integrity protected.

The unprotected JWS `header` member MUST NOT be present in the Tilden v1 signed-resolution profile.

## 8. Algorithm profile

### 8.1 Required algorithm

The Tilden v1 signed-resolution profile uses the fully specified JOSE algorithm identifier:

```text
Ed25519
```

as registered by RFC 9864.

Conforming v1 signers MUST produce `Ed25519` signatures.

Conforming v1 verifiers MUST support `Ed25519` verification.

The older polymorphic JOSE identifier `EdDSA` MUST NOT be produced by this profile.

Future Tilden specifications MAY define additional fully specified algorithms.

### 8.2 Forbidden algorithms

The following MUST NOT be accepted for Tilden federation signatures:

- `none`;
- symmetric MAC algorithms;
- an algorithm not explicitly permitted by the active Tilden cryptographic profile;
- an algorithm inconsistent with the delegated public key.

A verifier MUST treat the protected `alg` value as an input to policy validation, not as an instruction to accept any algorithm supported by its crypto library.

## 9. Key representation and binding

For `Ed25519`, the matching TILDEN-AUTH-003 signing-key entry SHOULD use a public JWK representation containing at least:

```json
{
  "kid": "2026-09-a",
  "alg": "Ed25519",
  "kty": "OKP",
  "crv": "Ed25519",
  "x": "<base64url public key>"
}
```

The `kid` in the protected JWS header MUST match exactly one currently authorized signing key in the selected Authority Delegation Object.

The delegated key MUST be structurally compatible with the protected `alg` value.

A key match by `kid` alone is insufficient if the key type, curve, or algorithm policy is inconsistent.

## 10. No key discovery from the signed object

A Tilden signed Resolution Object MUST NOT use JOSE header parameters to introduce a new trust key.

A verifier MUST reject a signed resolution object whose JOSE header contains any of the following:

- `jku`;
- `jwk`;
- `x5u`;
- `x5c`;
- another extension whose effect is to supply or redirect trust to signer-controlled key material.

This prevents key-substitution attacks in which an attacker signs a forged object with its own key and then supplies that key alongside the signature.

The verification key comes from the already-authenticated TILDEN-AUTH-003 delegation path.

## 11. Signing procedure

A conforming resolver producing a signed object MUST:

1. construct a Tilden Resolution Object that conforms to TILDEN-CORE-001;
2. ensure the `subject` falls within its active delegation scope;
3. ensure the resolution object's `authority` matches the active delegated resolver;
4. choose an Ed25519 key currently authorized by the active delegation;
5. construct the protected JOSE header required by Section 7;
6. encode the protected header and payload according to RFC 7515;
7. sign the resulting JWS Signing Input with the selected private key;
8. return the Flattened JWS JSON Serialization.

The private signing key MUST NOT be exposed through Tilden resolution, bootstrap, logging, telemetry, or error responses.

## 12. Verification procedure

A conforming client verifying a signed Resolution Object MUST perform the following checks in order:

1. canonicalize the requested subject under TILDEN-CORE-001;
2. obtain and authenticate the current Authority Delegation Object under TILDEN-AUTH-003;
3. confirm the delegation is currently valid and not revoked;
4. parse the outer JWS structure without trusting its payload;
5. require the protected `typ`, `cty`, `alg`, and `kid` values defined by this profile;
6. reject forbidden or unprotected key-discovery parameters;
7. locate the `kid` in the current delegation's `signing_keys`;
8. validate algorithm and public-key compatibility;
9. verify the JWS signature over the exact JWS Signing Input;
10. only after successful signature verification, decode and parse the payload as JSON;
11. validate the payload as a Tilden Resolution Object;
12. confirm the payload `subject` equals the requested canonical subject;
13. confirm the payload `authority` equals the resolver authorized by the active delegation;
14. confirm `issued_at` and `expires_at` satisfy the active delegation and local freshness policy;
15. apply the capability-selection rules from TILDEN-CORE-001.

Failure at any security-relevant verification step MUST fail closed for Tilden resolution.

## 13. Current authorization at time of use

A client MUST evaluate signer authorization against the **current accepted delegation state at the time the object is used for a new session**, not merely against historical state at the time the object was issued.

Therefore, a cached object that remains cryptographically valid MUST nevertheless be rejected when:

- its signing key has been revoked;
- a resolver transfer has removed that key from authority;
- the delegation has expired;
- a higher valid delegation serial supersedes the key and no longer authorizes it;
- local policy has withdrawn trust in the delegation source.

This rule permits emergency key revocation and provider transfer to invalidate still-unexpired cached resolution objects.

## 14. Freshness and replay

The `issued_at` and `expires_at` fields remain part of the signed payload and therefore are integrity protected.

A verifier MUST reject a signed object when:

- `expires_at` is in the past;
- `issued_at` is later than `expires_at`;
- `issued_at` is unreasonably in the future beyond permitted clock skew;
- the object's lifetime exceeds the maximum allowed by active delegation policy or local policy.

The reference profile RECOMMENDS a maximum resolution-object lifetime of 900 seconds unless a stricter delegation policy applies.

A valid signature does not make an expired route current.

## 15. Relationship to delegation lifetime

A signed Resolution Object MUST NOT outlive the authority under which it was signed.

A resolver MUST NOT issue an object whose `expires_at` is later than the active delegation's `valid_until`.

A verifier MUST reject such an object even when the signature itself verifies.

## 16. Key rotation

During an AUTH-003 key-rotation overlap, a resolver MAY sign new objects with either currently authorized key.

Example:

```text
delegation serial 42: key A + key B

object 1 -> key A
object 2 -> key B
```

A v1 Resolution Object carries exactly one signature. Multi-signature JWS is intentionally outside this profile.

Once a newer accepted delegation removes key A, objects signed by key A MUST NOT be used for new sessions even if their `expires_at` value has not yet passed.

## 17. Resolver transfer

When subject authority transfers from resolver A to resolver B:

1. AUTH-003 establishes the transfer through a newer valid delegation;
2. resolver A's removed signing keys cease to authorize new Tilden resolution;
3. cached objects signed only by removed resolver-A keys fail current-authorization checks;
4. resolver B signs new objects using keys authorized by the new delegation.

No HTTP redirect, DNS response, or valid old signature can independently transfer Tilden subject authority.

## 18. Caching and federation

Signed Resolution Objects MAY be cached or forwarded by intermediaries without trusting those intermediaries to preserve object integrity.

An intermediary MAY change transport metadata such as HTTP cache headers, but MUST NOT modify the protected JWS header, encoded payload, or signature.

A client receiving a signed object from a cache, federation peer, message bus, or offline store MUST perform the same AUTH-003 and SIGN-004 verification required for a directly fetched object.

The transport source is not automatically the signer and is not automatically authoritative.

## 19. TLS remains required for live resolution

Independent object signatures do not remove the requirement for authenticated TLS in the HTTPS reference profile.

TLS protects:

- request confidentiality where applicable;
- transport integrity;
- resolver-origin authentication;
- operational metadata not covered by the object signature.

JWS protects the Resolution Object itself across transport boundaries.

The two mechanisms are complementary.

## 20. Failure classes

Implementations SHOULD distinguish at least:

- `unsigned-object` — a signature was required but absent;
- `malformed-jws` — the envelope or encoding is invalid;
- `unsupported-algorithm` — `alg` is not permitted by the active profile;
- `unknown-kid` — the signing key is not in the current delegation;
- `key-mismatch` — key type or curve is inconsistent with `alg`;
- `forbidden-key-source` — the JWS attempts signer-controlled key discovery;
- `bad-signature` — cryptographic verification failed;
- `subject-mismatch` — signed payload does not match the requested subject;
- `authority-mismatch` — signed payload names the wrong resolver authority;
- `expired-object` — payload freshness window has ended;
- `future-object` — issuance time exceeds allowed clock skew;
- `object-too-long-lived` — lifetime violates delegation or local policy;
- `delegation-invalid` — current authority state is expired, revoked, or otherwise invalid;
- `signer-no-longer-authorized` — the object verifies cryptographically but the key has lost current authority.

Error responses MUST NOT expose private key material or sensitive authority-enrollment evidence.

## 21. Security considerations

### 21.1 Algorithm confusion

An attacker attempts to make a verifier interpret the same key under a weaker or unintended algorithm.

**Mitigation:** v1 fixes `alg` to the fully specified `Ed25519` identifier and requires key/algorithm compatibility checks.

### 21.2 Key substitution

An attacker supplies a forged object and embeds or links to its own verification key.

**Mitigation:** `jku`, `jwk`, `x5u`, `x5c`, and equivalent signer-controlled key sources are forbidden. Keys come only from authenticated AUTH-003 delegation state.

### 21.3 Replay

An attacker replays an old but correctly signed route.

**Mitigation:** signed freshness fields, short lifetimes, current-delegation checks, revocation, and serial-based authority updates.

### 21.4 Compromised signing key

An attacker obtains a resolver private key.

**Mitigation:** AUTH-003 key rotation and revocation, short resolution lifetimes, secure key custody, and current-authorization verification.

### 21.5 Compromised cache or intermediary

An intermediary alters routes or capabilities.

**Mitigation:** JWS verification over the exact payload bytes.

### 21.6 Valid signature from wrong authority

An attacker has a valid Tilden signing key for some other number or prefix.

**Mitigation:** verify subject scope and resolver authority against the active delegation before accepting the payload.

## 22. Privacy considerations

Signing a Resolution Object makes its contents tamper-evident; it does not make them confidential.

Resolvers MUST continue the metadata-minimization requirements of TILDEN-CORE-001.

Sensitive device identifiers, carrier credentials, account identifiers, eSIM secrets, private accessibility data, and other unnecessary subscriber information MUST NOT be placed in a public signed Resolution Object merely because the object is cryptographically protected.

## 23. Reference example

Given an AUTH-003 delegation containing:

```json
{
  "kid": "2026-09-a",
  "alg": "Ed25519",
  "kty": "OKP",
  "crv": "Ed25519",
  "x": "xJUx6jfXHWU2fB4_sXO6_Iz7MlBY-MfYO_idoXZkYJM"
}
```

a resolver may return a Flattened JWS whose protected header decodes to:

```json
{
  "alg": "Ed25519",
  "kid": "2026-09-a",
  "typ": "tilden-resolution+jws",
  "cty": "application/tilden+json"
}
```

and whose payload decodes to the ordinary `examples/resolution.json` object.

The corresponding complete test object is maintained in `examples/signed-resolution.jws.json`.

## 24. Design invariant

The complete Tilden trust path is:

```text
identity
  -> bootstrap trust
  -> subject delegation
  -> authorized signer
  -> verified resolution
  -> selected endpoint
  -> independently authenticated session
```

No step implies the next without explicit verification.

The result preserves Tilden's core rule:

> **One number. Every modality.**
