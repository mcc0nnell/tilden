# ADR 0006: Selection is an evidence artifact, not runtime state

Status: Accepted for Draft 0.1

## Context

`TILDEN-REQUEST-001` defines deterministic endpoint selection, but a selected URI alone is insufficient for assurance, debugging, or conformance. A relying party needs to know which exact inputs were evaluated, which candidates failed hard constraints, which preferences affected ranking, and why the winner was chosen.

Copying the entire ephemeral request into persistent evidence would create unnecessary privacy risk because request parameters may reveal language, relay, or accessibility needs.

## Decision

Tilden defines a separate `TildenSelection` evidence artifact.

The artifact:

- binds to the exact validated resolution and ephemeral request by digest;
- records deterministic candidate outcomes and preference scores;
- records the selected endpoint or typed terminal failure;
- normally records capability IDs rather than private request parameter values;
- ends before Baudot or another runtime begins signaling/media negotiation.

The full `TildenRequest` is not embedded in the selection artifact.

## Consequences

Selection behavior becomes independently testable and reproducible.

WindAnvil or another assurance system can correlate resolution, request, selection, and runtime evidence without requiring every artifact to contain every other artifact.

Baudot receives a clean selected endpoint and may correlate its runtime transcript using the selection identifier, but Tilden selection evidence does not become SIP, WebRTC, SDP, RTP, or media state.

A future profile may sign or attest the evidence record when it crosses administrative trust boundaries.
