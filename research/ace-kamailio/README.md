# ACE Kamailio routing donor mocks

This directory contains deterministic offline fixtures derived from the pinned public ACE Direct Kamailio deployment as a **research donor**, not a protocol dependency.

Run:

```bash
python research/ace-kamailio/mock_router.py
```

The vectors cover:

- external INVITE dispatch across multiple candidate media servers;
- deterministic next-candidate selection;
- skipping an unavailable candidate;
- explicit route exhaustion;
- source-role separation for traffic already coming from the media-server cluster;
- registration forwarding as a distinct operation; and
- non-INVITE traffic remaining outside the media-server dispatch decision.

All endpoint names use the reserved `.example` namespace. The model does not open sockets, query DNS, start Kamailio/Asterisk/rtpengine, or claim current VRS routing behavior.

See [`../../docs/provenance/ace-direct-kamailio-routing.md`](../../docs/provenance/ace-direct-kamailio-routing.md) for the evidence boundary.
