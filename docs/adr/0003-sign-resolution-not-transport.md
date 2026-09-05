# ADR 0003: Sign the resolution object, not only the transport

Status: Accepted for Draft 0.1

## Context

Tilden assertions may be cached, forwarded, recorded as evidence, or consumed by runtimes other than the service that originally retrieved them. Transport security such as TLS or DNSSEC can authenticate a retrieval path, but it does not make the resolution object independently verifiable after that path ends.

## Decision

Tilden signs the `TildenResolution` payload itself.

Draft 0.1 uses:

- RFC 8785 JSON Canonicalization Scheme for deterministic payload bytes;
- RFC 7515 JSON Web Signature for the signature envelope;
- explicit identity, authority, key, and expiry checks in addition to signature verification.

The signature proof remains outside the signed payload to avoid recursive signing. The signed resolution carries the trust profile and key identifier.

## Consequences

- Cached or forwarded assertions remain independently verifiable.
- WindAnvil or another assurance system can retain the original proof as evidence.
- Baudot can consume only the validated resolution and does not need JOSE state in its signaling layer.
- A cryptographically valid signature is insufficient unless the signer is authorized by the discovery chain.
- Deployments need explicit key publication, rotation, revocation, and algorithm policy.

## Rejected alternatives

### Trust TLS alone

Rejected because trust would disappear once the response leaves the authenticated transport and evidence could not be independently replayed or verified.

### Put the signature inside the signed object

Rejected because this creates a recursive representation problem and complicates deterministic verification.

### Trust any cryptographically valid signer

Rejected because key validity does not establish authority over an identity or namespace.
