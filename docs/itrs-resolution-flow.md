# iTRS resolution flow

This flow shows how a Tilden deployment can consume the FCC TRS Numbering Directory without turning the directory into a public service or moving signaling/media into Tilden.

```text
1. incoming call/session
        |
        v
2. Tilden receives identifier + call context
        |
        v
3. resolver determines that the iTRS profile applies
        |
        v
4. protected iTRS adapter constructs authorized directory query
        |
        | calling TN
        | called TN
        | service: VRS | IP Relay
        | direction: inbound | outbound
        v
5. TRS Numbering Directory
        |
        | routing URI
        | transaction identifier
        v
6. adapter normalizes authoritative result
        |
        v
7. Tilden emits short-lived resolution object
        |
        v
8. Baudot / endpoint stack establishes session
```

## Boundary conditions

- The public resolver does not expose the TRS Numbering Directory directly.
- The protected adapter holds whatever access controls are required by the TRS Numbering Administrator.
- A routing URI returned by the directory is treated as authoritative input, not as a hint to be rewritten into a different provider route.
- The directory transaction identifier remains protected provenance unless disclosure is explicitly authorized.
- Tilden does not bulk-copy directory records.
- Tilden does not expose URD subscriber-registration data.
- Tilden may add transport-neutral capability metadata only when that metadata is independently justified by the resolved route or local policy.

## Fallback

If an authorized iTRS query returns no route, policy may evaluate a different route class, such as PSTN. If the query fails because the adapter is unavailable or unauthorized, the resolver must distinguish that failure from an authoritative negative result.

This distinction prevents an infrastructure failure from being mistaken for evidence that the called number is not an iTRS number.
