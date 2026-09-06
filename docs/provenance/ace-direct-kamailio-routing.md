# ACE Direct Kamailio routing donor

Status: **non-normative research provenance**

This note preserves public ACE Direct Kamailio behavior as a scenario donor for Tilden. It does not copy the deployment as a Tilden protocol and it makes no claim about any current production VRS route.

## Pinned source

```text
repository: mitre-ace-direct/kamailio
commit:     3c56fc4112680a15cedd4ece835a9f371f079e0b
kamailio.cfg blob: 47f0af82f3c5a713e2bf7ae1e15023507e588e8d
README.md blob:    bcc9b691e941ad1760b350dfd6a1aca04ad1fc80
observed:   2026-09-05
```

The pinned configuration is a large deployment artifact. Tilden preserves only the state transitions that are useful to federation design.

## Observed routing state machine

The ACE configuration distinguishes traffic arriving from its Asterisk/media-server cluster from traffic arriving from outside. With dispatcher support enabled, `FROMASTERISK` recognizes a source in the dispatcher list. New external `INVITE` requests are sent through `TOASTERISK`, where `ds_select_dst("1", "4")` selects a destination from dispatcher group 1 using the configured round-robin algorithm. If no destination is available, that path returns a service-unavailable failure rather than inventing a route.

Conceptually:

```text
incoming SIP request
      |
      +-- source belongs to media-server cluster
      |       -> treat as inside route
      |
      `-- external new INVITE
              -> select media-server destination
              -> no destination: explicit routing failure
              -> destination selected: relay toward selected server
```

Registration forwarding is a distinct path. `REGFWD` also uses the dispatcher list and forwards `REGISTER` information toward an Asterisk destination rather than treating registration and call routing as one operation.

## Media anchoring is a separate decision

The same configuration loads Kamailio's `rtpengine` module when NAT support is enabled and points it at a local control socket (`udp:127.0.0.1:12221`). SDP-bearing dialog traffic can invoke `rtpengine_manage()`, including INVITE/ACK and reply paths, while BYE handling includes relay cleanup behavior.

That is useful evidence for the architecture boundary, but **media anchoring is not Tilden resolution behavior**. Tilden may identify candidate endpoints and routing metadata. A runtime such as Baudot decides whether signaling and media can actually traverse a proxy/relay path and owns the evidence for that decision.

## Concepts worth retaining

The donor supports several implementation-neutral concepts:

1. **Endpoint sets can contain multiple eligible destinations.** A resolution object should not assume exactly one backend.
2. **Selection and reachability are separate facts.** Selecting a candidate route does not prove it is healthy or interoperable.
3. **No route is an explicit result.** Consumers must not silently synthesize a destination when the authoritative candidate set is exhausted.
4. **Source role matters.** Traffic from a trusted federation/media-server domain can follow a different policy from unauthenticated external traffic.
5. **Registration/discovery and session routing are different operations.** They may share endpoint data without sharing lifecycle semantics.
6. **Media relay policy belongs after resolution.** Discovery success must not imply RTP/RTT/video relay success.

## Deployment details that are not protocol requirements

Tilden does **not** inherit these ACE implementation choices:

- dispatcher group number `1`;
- Kamailio algorithm number `4`;
- round-robin as a mandatory selection policy;
- Asterisk as a mandatory backend;
- the local rtpengine control port `12221`;
- TCP forcing, WebSocket workarounds, NAT helper flags, or dialog-variable conventions;
- trusted-source bypass rules;
- any specific SIP status code used by the historical deployment when a route is unavailable.

Those are implementation evidence, not Tilden semantics.

## Offline donor mocks

`research/ace-kamailio/mock-vectors.json` and `mock_router.py` preserve the useful control-flow concepts without running Kamailio, Asterisk, rtpengine, or any external network service.

The mock lane is deliberately `.example`-only and deterministic. It checks candidate selection, source-role separation, registration forwarding, and explicit exhaustion behavior. It does not claim Kamailio conformance or current ACE Direct behavior beyond the pinned donor source.
