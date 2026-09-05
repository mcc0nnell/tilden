# TILDEN-TRUST-001: Signed Resolution Trust Profile

Status: **Draft 0.1**  
Specification ID: `TILDEN-TRUST-001`  
Depends on: `TILDEN-CORE-001`, `TILDEN-DISCOVERY-001`

## 1. Purpose

This specification defines how a Tilden resolution is cryptographically bound to the identity and authority discovered for it.

Discovery proves where an assertion came from. Trust proves that the assertion itself has not been altered, substituted for another identity, or accepted from an unauthorized signer.

## 2. Security boundary

Tilden distinguishes transport authentication from assertion authentication.

TLS, DNSSEC, authenticated directories, and similar mechanisms may protect discovery hops, but a portable or cached `TildenResolution` SHOULD remain independently verifiable after retrieval.

The trust profile therefore signs the resolution object itself.

```text
requested identity
      |
      v
authenticated discovery chain
      |
      v
signed TildenResolution
      |
      +--> identity binding
      +--> authority binding
      +--> key binding
      +--> freshness check
      `--> signature verification
              |
              v
      validated TildenResolution
              |
              v
            Baudot
```

## 3. Signed payload

The signed payload is a schema-valid `TildenResolution` serialized using the JSON Canonicalization Scheme defined by RFC 8785.

The canonical payload MUST include at least:

- `version`;
- `canonicalIdentity`;
- `authority`;
- `endpoints`;
- `capabilities`;
- `trust` metadata;
- `expiresAt`.

The `trust.proof` field MUST be absent from the signed payload when the proof is carried by the JWS envelope. This avoids recursive signing.

The `trust.profile` value for this draft is `tilden-jws-jcs-0.1`.

## 4. Signature envelope

The canonicalized resolution bytes are the payload of a JSON Web Signature as defined by RFC 7515.

The JWS protected header MUST contain:

- `alg` — the signature algorithm;
- `kid` — the signer key identifier;
- `typ` — `tilden-resolution+jws`.

The `kid` value MUST match `trust.keyId` in the signed resolution.

The final transport representation MAY use JWS Compact Serialization or JWS JSON Serialization. A profile that permits both MUST define deterministic acceptance and evidence rules.

## 5. Algorithm policy

The baseline federation profile requires asymmetric digital signatures.

- `alg=none` MUST NOT be accepted.
- symmetric MAC algorithms MUST NOT be used for cross-organization federation assertions because verifier possession of a shared secret would also permit assertion creation;
- deployments MUST define an explicit algorithm allow-list;
- algorithm acceptance MUST be based on local/profile policy, not solely on the value supplied by the untrusted JWS header.

Draft 0.1 deliberately does not select a single mandatory-to-implement asymmetric algorithm. That decision requires deployment evidence across browser, server, government, telecom, and constrained environments.

## 6. Identity binding

After signature verification, the relying resolver MUST compare the signed `canonicalIdentity` with the canonical identity produced from the original request.

The values MUST match exactly according to the active identifier profile.

A valid signature over a different identity is not a successful resolution and MUST be reported as an identity-binding failure.

## 7. Authority binding

A valid signature does not by itself establish authority.

The signer key MUST be authorized by the authority chain produced by `TILDEN-DISCOVERY-001` to make assertions for the requested identity.

The signed `authority.id` MUST be consistent with that chain. If `authority.delegatedBy` is present, the delegation MUST be supported by the discovery evidence or another active trust profile.

A resolver MUST NOT accept a signer merely because its key is cryptographically valid.

## 8. Key binding and rotation

`kid` is a key identifier, not a trust anchor.

The active discovery/trust profile MUST define how a `kid` maps to a verification key and how that key is bound to the discovered authority.

Key resolution MUST NOT introduce a new unauthenticated authority hop.

Profiles MUST define:

- key publication or retrieval;
- key rotation behavior;
- revocation or emergency withdrawal behavior;
- overlap rules during planned rotation;
- cache lifetime for key material.

A previously valid key MUST NOT remain trusted indefinitely because a cached assertion once verified successfully.

## 9. Freshness and replay

The signed `expiresAt` value is part of the cryptographic payload and MUST be enforced.

The effective lifetime of a trusted result MUST also respect any earlier expiry imposed by the discovery chain, key material, certificate, or active trust profile.

A signed resolution replayed after its effective expiry MUST be rejected as `expired` even if the signature remains mathematically valid.

Profiles MAY impose a maximum assertion lifetime shorter than `expiresAt`.

## 10. Proof handling

A resolver MAY preserve the original JWS as evidence after successful verification.

Baudot does not need the raw proof in order to negotiate a session. The preferred handoff is a validated `TildenResolution` plus, when requested by policy, a reference or digest linking the runtime decision to retained trust evidence.

This prevents cryptographic envelope details from becoming signaling state.

## 11. Failure semantics

Trust-aware resolvers SHOULD distinguish at least:

- `signature_invalid`;
- `algorithm_disallowed`;
- `key_unavailable`;
- `key_untrusted`;
- `identity_mismatch`;
- `authority_mismatch`;
- `expired`;
- `revoked`;
- `malformed_proof`.

Security-sensitive evidence MUST NOT collapse these failures into `not_found`.

## 12. Downgrade resistance

If a profile requires signed assertions, failure to verify a signature MUST NOT cause silent fallback to an unsigned resolution for the same identity.

A deployment MAY explicitly configure a legacy unsigned mode, but the result MUST be distinguishable from a verified Tilden federation assertion and MUST NOT inherit verified trust status.

## 13. Privacy

Signatures provide integrity and authenticity, not confidentiality.

A signed Tilden resolution may still expose routing or accessibility metadata to anyone able to retrieve it. Discovery profiles SHOULD minimize disclosure and MAY use authenticated or access-controlled retrieval where user-specific capability data is sensitive.

Encryption of resolution assertions is outside Draft 0.1.

## 14. Conformance

A conforming verifier for `tilden-jws-jcs-0.1` MUST:

1. validate the JWS structure;
2. enforce an explicit algorithm allow-list;
3. reject `none` and symmetric federation assertions;
4. resolve `kid` only through an authority-bound mechanism;
5. verify the signature over the canonicalized resolution payload;
6. require `kid` to match `trust.keyId`;
7. bind `canonicalIdentity` to the original request;
8. bind the signer and signed authority to the discovery chain;
9. enforce effective expiry and revocation policy;
10. preserve typed trust failures;
11. return the inner `TildenResolution` only after all required checks succeed.

## 15. References

- RFC 7515 — JSON Web Signature (JWS)
- RFC 8785 — JSON Canonicalization Scheme (JCS)

## 16. Open questions

Draft 0.1 intentionally leaves open:

- the mandatory-to-implement asymmetric algorithm set;
- whether JWS Compact or JSON Serialization becomes the federation baseline;
- standard key publication for domain authorities;
- trust-anchor distribution for national numbering authorities;
- cross-jurisdiction authority delegation;
- certificate transparency or equivalent accountability mechanisms;
- confidential/encrypted discovery assertions.
