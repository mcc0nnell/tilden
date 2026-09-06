# ACE iTRS donor mocks

This directory preserves a deterministic, offline model of the useful resolution stages observed in the public ACE Direct iTRS integration.

It is **not** a production iTRS client and must never query current provider infrastructure.

## Run

```bash
python research/ace-itrs/mock_resolver.py
```

The mock consumes `mock-vectors.json` and checks six source-derived state-machine cases:

1. direct `E2U+sip` discovery in simple mode;
2. one alias hop before `E2U+sip` discovery;
3. no discovery result;
4. full NAPTR-to-SRV routing;
5. discovery succeeds but transport NAPTR is unavailable; and
6. transport NAPTR succeeds but no SRV route is available.

Reserved `.example` names are used throughout. No vector asserts that a real number or provider currently resolves through iTRS.

## Deliberate abstraction

The mock preserves state transitions, not shell mechanics. It does not emulate `dig`, `host`, `grep`, `awk`, `cut`, stdout token positions, or provider-specific configuration.

The historical script attempts a port-5060 fallback when transport NAPTR resolution fails. The mock records `fallbackAttempted=true` but deliberately does not synthesize a successful route from that fact. This keeps an observed legacy policy separate from a modern Tilden routing assertion.

See [`docs/provenance/ace-direct-itrs-resolution.md`](../../docs/provenance/ace-direct-itrs-resolution.md) for the pinned donor sources and the mapping to `TILDEN-CORE-001`.
