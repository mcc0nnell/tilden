# ADR 0005: Keep call requirements ephemeral

Status: Accepted for Draft 0.1

## Context

Tilden needs a way for a caller to express per-call requirements such as signed-language video, RTT, or E2EE. Publishing those preferences into directory records would create unnecessary privacy and linkability risks and would confuse durable reachability metadata with transient caller intent.

## Decision

`TildenRequest` is a separate, short-lived object used locally for endpoint selection.

Draft 0.1 fixes its scope to `local-selection` and intentionally omits a required caller identity field. Public directories MUST NOT store or publish requests as part of normal resolution data.

Wire transport, signing, selective disclosure, and remote negotiation are deferred to later profiles.

## Consequences

- accessibility requirements can influence routing without becoming durable directory metadata;
- callers can express hard requirements and soft preferences independently of provider records;
- the resolver remains authoritative for the target identity while the request remains caller policy;
- Baudot receives only the selected route and constraints necessary for runtime work;
- later federation protocols may define privacy-preserving disclosure without changing the basic resolution object.
