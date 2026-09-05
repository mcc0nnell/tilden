# TILDEN-SELECTION-001: Deterministic Endpoint Selection Evidence

Status: **Draft 0.1**  
Specification ID: `TILDEN-SELECTION-001`

## 1. Purpose

`TildenSelection` is the canonical evidence record produced when a Tilden selector evaluates a validated `TildenResolution` against a valid `TildenRequest`.

It answers a narrow but important question:

> Given these exact resolution and request inputs, why was this endpoint selected, or why was no endpoint acceptable?

The record is designed for reproducible conformance testing, operational diagnostics, and assurance systems such as WindAnvil. It is not a signaling message and does not replace the underlying resolution, request, or runtime negotiation evidence.

## 2. Position in the stack

```text
validated TildenResolution
          +
     TildenRequest
          |
          v
 deterministic selector
          |
          v
    TildenSelection
     |- input digests
     |- candidate decisions
     |- selected endpoint
     `- terminal result
          |
          v
     Baudot / runtime
```

A successful selection means only that an endpoint satisfies Tilden pre-session policy. Baudot or another runtime still determines whether the actual call can be established.

## 3. Core invariants

A conforming selection record MUST be:

1. **deterministic** — equal validated inputs and equal selection policy produce the same result;
2. **input-bound** — the record identifies the exact resolution and request inputs by digest;
3. **explainable** — every evaluated candidate has a machine-readable outcome;
4. **privacy-minimizing** — the evidence does not automatically embed the full ephemeral request;
5. **runtime-independent** — it ends before SIP, WebRTC, SDP, RTP, RTT, media, or security negotiation.

## 4. Object shape

The normative machine-readable form is `schemas/tilden-selection.schema.json`.

A selection record contains:

- `version`: selection object version;
- `selectionId`: opaque identifier for this decision;
- `target`: canonical identity being selected for;
- `resolutionDigest`: digest binding to the exact validated `TildenResolution`;
- `requestDigest`: digest binding to the exact `TildenRequest`;
- `evaluatedAt`: decision timestamp;
- `candidates`: ordered evidence for each endpoint evaluated;
- `terminal`: final selection result;
- `selectedEndpoint`: endpoint URI when `terminal` is `selected`.

Example:

```json
{
  "version": "0.1",
  "selectionId": "sel-7mC1vN4X1q9zR2Lp",
  "target": "tel:+33123456789",
  "resolutionDigest": "sha256:resolution-example",
  "requestDigest": "sha256:request-example",
  "evaluatedAt": "2026-09-05T22:20:00Z",
  "candidates": [
    {
      "uri": "sip:plain@example.net",
      "priority": 1,
      "preferenceScore": 0,
      "outcome": "eligible",
      "matchedPreferred": []
    },
    {
      "uri": "sip:secure@example.net",
      "priority": 10,
      "preferenceScore": 100,
      "outcome": "selected",
      "matchedPreferred": ["security.e2ee"]
    }
  ],
  "terminal": "selected",
  "selectedEndpoint": "sip:secure@example.net"
}
```

## 5. Input binding

`resolutionDigest` and `requestDigest` bind the decision to exact canonical input objects.

Draft 0.1 does not freeze the digest algorithm or canonicalization representation. An active profile that emits selection evidence MUST define both and MUST use the same representation consistently for generation and verification.

A verifier MUST NOT accept a `TildenSelection` as evidence for different input objects merely because their target identity or selected endpoint happens to match.

## 6. Candidate evidence

The selector records each endpoint it actually evaluates in deterministic endpoint order.

Each candidate contains:

- `uri`;
- `priority` when asserted;
- `preferenceScore` after preferred-capability matching;
- `outcome`;
- optional `missingRequired` capability IDs;
- optional `matchedExcluded` capability IDs;
- optional `matchedPreferred` capability IDs.

Draft 0.1 candidate outcomes are:

- `rejected-required` — at least one required capability did not match;
- `rejected-excluded` — at least one excluded capability matched;
- `eligible` — candidate passed hard constraints but was not selected;
- `selected` — candidate won deterministic ranking.

An endpoint MUST NOT be marked `eligible` or `selected` when it fails a required or excluded constraint.

## 7. Evidence minimization

Capability IDs are normally sufficient to explain selection behavior.

A selection record SHOULD NOT copy full capability parameter values from the request into candidate evidence. In particular, language, relay, disability-related, or preference details SHOULD remain in the ephemeral request unless a conformance or incident investigation requires greater detail.

For example, evidence may record that `video.sign` failed without automatically recording the requested signed language.

Implementations MAY retain a more detailed private diagnostic record locally. That record is outside Draft 0.1 and MUST NOT be assumed safe for broad export.

## 8. Deterministic selection procedure

`TILDEN-SELECTION-001` uses the selection semantics defined by `TILDEN-REQUEST-001` and makes the resulting decision observable.

For each endpoint, a conforming selector MUST:

1. evaluate required capability entries;
2. record failed required capability IDs;
3. evaluate excluded capability entries;
4. record matched exclusion capability IDs;
5. compute the sum of matched preferred weights for otherwise acceptable candidates;
6. record matched preferred capability IDs;
7. rank acceptable candidates by higher preference score first;
8. break ties by lower endpoint priority first;
9. break remaining ties by lexicographic endpoint URI order;
10. mark exactly one candidate `selected` when at least one acceptable candidate exists.

The selector MUST produce identical candidate outcomes and selected URI for identical inputs and policy.

## 9. Candidate ordering

The `candidates` array is evidence, not an unordered set.

Draft 0.1 requires candidates to be emitted in deterministic evaluation order: ascending endpoint priority, then lexicographic endpoint URI, unless a future profile defines another canonical ordering.

Ranking may select a later candidate because preferred capability score outranks priority. Evidence order and winning rank are intentionally separate concepts.

## 10. Terminal results

Draft 0.1 terminal values are:

- `selected`;
- `no_capable_endpoint`;
- `target_mismatch`;
- `resolution_mismatch`;
- `expired_request`;
- `invalid_request`.

When `terminal` is `selected`, `selectedEndpoint` MUST be present and exactly one candidate MUST have `outcome: selected`.

When `terminal` is not `selected`, `selectedEndpoint` MUST be absent and no candidate may have `outcome: selected`.

A target, digest, freshness, or request-validity failure may occur before endpoint evaluation. In those cases `candidates` MAY be empty.

## 11. Failure versus rejection

Candidate rejection and terminal failure are different concepts.

`rejected-required` and `rejected-excluded` describe why one endpoint was unusable. `no_capable_endpoint` means all evaluated endpoints were rejected.

`target_mismatch`, `resolution_mismatch`, `expired_request`, and `invalid_request` describe failures of the selection operation itself and SHOULD occur before candidate ranking.

These are still pre-session failures. They MUST NOT be represented as SIP response codes, WebRTC errors, media failures, or Baudot runtime negotiation failures.

## 12. Baudot handoff

When `terminal` is `selected`, Baudot SHOULD receive:

- the selected endpoint;
- the validated `TildenResolution` or the relevant validated endpoint object;
- only request constraints needed by runtime policy;
- the `selectionId` or selection digest when evidence correlation is useful.

Baudot MUST NOT treat a successful `TildenSelection` as proof of signaling, media, accessibility, or security interoperability.

## 13. WindAnvil handoff

A `TildenSelection` is suitable as an assurance artifact because it binds a decision to exact inputs and records deterministic reasoning.

An assurance system may store:

```text
resolution digest
request digest
selection record
Baudot session evidence
conformance results
```

This permits later verification that routing policy selected the expected endpoint independently of whether runtime negotiation succeeded.

The full private `TildenRequest` SHOULD NOT be exported merely because its digest appears in the selection record.

## 14. Integrity and signing

Draft 0.1 does not require the selection record itself to be signed.

Deployments that use selection evidence across administrative trust boundaries SHOULD bind it to an authenticated evidence envelope or provenance system. A future profile may reuse Tilden trust primitives or an external attestation format.

Signing a selection record does not make an incorrect selection algorithm correct; conformance remains independently testable.

## 15. Conformance

A conforming selector MUST:

1. produce a schema-valid `TildenSelection`;
2. bind the exact resolution and request inputs by digest;
3. emit deterministic candidate ordering;
4. record missing required capability IDs for required-capability rejection;
5. record matched excluded capability IDs for exclusion rejection;
6. compute preferred scores deterministically;
7. mark no more than one candidate selected;
8. make `selectedEndpoint` agree with the selected candidate;
9. avoid copying unnecessary private request parameters into the evidence record;
10. distinguish selection outcomes from runtime failures.

Executable fixtures belong under `conformance/selection/`.

## 16. Open questions

Draft 0.1 deliberately leaves open:

- canonical digest algorithm and canonicalization profile;
- whether selection records need a signed evidence envelope;
- how much parameter-level diagnostic detail may be safely exported;
- cross-provider retention requirements;
- emergency-routing evidence requirements;
- group-call and multi-target selection evidence;
- whether endpoint cost, jurisdiction, or policy metadata belongs in a later ranking profile;
- whether a standardized evidence bundle should directly connect TildenSelection to Baudot and WindAnvil artifacts.
