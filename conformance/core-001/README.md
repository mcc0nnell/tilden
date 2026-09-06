# TILDEN-CORE-001 conformance

This directory defines executable fixture categories for the core resolution contract.

Initial cases:

1. **valid-minimal** — schema-valid resolution with one endpoint, explicit authority, trust profile, and expiry.
2. **valid-multimodal** — endpoint advertises multiple accessible modalities.
3. **invalid-expired** — consumer must reject or refresh an expired result.
4. **invalid-untrusted** — trust validation failure must remain distinct from `not_found`.
5. **invalid-schema** — consumer must reject malformed resolution objects.
6. **identifier-no-silent-rewrite** — resolver must not silently reinterpret an unsupported identifier scheme.
7. **endpoint-order-deterministic** — equal input and authority state produce deterministic endpoint ordering.

Fixtures should be transport-neutral. A DNS, HTTPS, ENUM-family, enterprise directory, or other discovery implementation may satisfy the same core cases when mapped into the normative resolution object.
