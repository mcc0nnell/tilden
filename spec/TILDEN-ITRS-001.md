# TILDEN-ITRS-001 — TRS Numbering Directory Query Profile

Status: Draft

## 1. Purpose

This profile defines how an authorized Tilden deployment may use the FCC Internet-based Telecommunications Relay Service (iTRS) TRS Numbering Directory as an authoritative routing input for numbers already provisioned in that directory.

Tilden does not replace the TRS Numbering Directory and does not expose it as a public lookup service. Instead, an authorized Tilden iTRS adapter performs a permitted directory query and translates the resulting routing information into a short-lived Tilden resolution object.

## 2. Architectural rule

For identifiers present in the TRS Numbering Directory:

> Query the authoritative iTRS routing system first; adapt the result second.

The iTRS directory remains authoritative for the routing information it is responsible for. Tilden adds protocol-neutral normalization, capability expression, policy, federation metadata, and downstream route selection.

```text
caller / communications gateway
            |
            v
       Tilden resolver
            |
            v
 authorized iTRS adapter
            |
            v
 TRS Numbering Directory Query Interface
            |
            v
 routing URI + transaction identifier
            |
            v
  Tilden resolution object
            |
            v
 Baudot / SIP / WebRTC / RTT / other transport
```

## 3. Access boundary

The TRS Numbering Directory is not a public directory.

An implementation conforming to this profile MUST NOT expose unrestricted public access to the underlying iTRS Query Interface.

The adapter MUST operate only under authority granted to an Internet-based TRS provider or other entity authorized by the FCC to access the TRS Numbering Directory.

Credentials, client certificates, source-IP restrictions, private network paths, or other access-control mechanisms used by the TRS Numbering Administrator MUST terminate at the protected adapter boundary and MUST NOT be forwarded to callers.

A public edge runtime such as a Cloudflare Worker MAY invoke a protected adapter, but MUST NOT embed long-lived iTRS administrative credentials in publicly deployable code or expose a pass-through query endpoint.

## 4. Query mapping

The current iTRS call-routing model supports a query containing at least:

- calling telephone number;
- called telephone number;
- service type, including VRS or IP Relay; and
- call direction, including inbound or outbound.

The authoritative query returns routing information and a unique transaction identifier for the query.

A Tilden request targeting the iTRS profile SHOULD therefore carry enough context to derive those fields.

Example logical request:

```json
{
  "identifier": "tel:+12025550142",
  "context": {
    "callingIdentifier": "tel:+14105550100",
    "service": "vrs",
    "direction": "inbound"
  },
  "acceptCapabilities": ["video", "asl", "sip"]
}
```

The exact transport representation used by the TRS Numbering Administrator is outside the Tilden protocol and MAY change independently.

## 5. Response translation

The adapter SHALL translate the authoritative iTRS routing response into a Tilden route without changing the routing target.

A returned SIP or other URI becomes a route target. The iTRS transaction identifier SHOULD be retained as protected provenance metadata for audit and troubleshooting but SHOULD NOT be exposed publicly unless policy authorizes disclosure.

Example normalized Tilden result:

```json
{
  "identifier": "tel:+12025550142",
  "authority": {
    "type": "fcc-itrs-directory",
    "profile": "tilden-itrs-001"
  },
  "routes": [
    {
      "uri": "sip:2025550142@example-vrs.invalid",
      "capabilities": ["video", "asl", "sip"],
      "source": "itrs"
    }
  ],
  "provenance": {
    "transactionRef": "protected",
    "freshness": "per-call"
  }
}
```

## 6. Freshness and caching

Because the TRS Numbering Directory participates in active call routing and reflects provider changes and porting state, a Tilden iTRS adapter SHOULD treat directory results as per-call routing information.

Implementations MUST NOT create a bulk mirror of records controlled by other providers.

If caching is used for resilience or latency, it MUST be short-lived, MUST respect administrator policy, and MUST NOT be used to bypass required per-call validation or query obligations.

## 7. Portability

The iTRS numbering system already tracks number-porting state and changes in provider control. Tilden SHOULD rely on the current authorized directory result rather than attempt to infer the destination from stale provider configuration.

This gives Tilden a simpler portability rule for iTRS numbers:

> The current authorized iTRS query result wins.

A Tilden resolver MUST NOT preserve an old provider route after the authoritative directory indicates a different routing target.

## 8. Reverse validation

The iTRS environment also supports reverse-validation use cases in which an IP address, user identifier, or screen name may be queried to validate registration and, where permitted, obtain the corresponding registered telephone number.

Tilden MAY define a separate authenticated reverse-validation operation, but such an operation MUST NOT be exposed as a general public identity-discovery service.

Reverse validation is out of scope for the public `resolve` operation defined by TILDEN-CORE-003.

## 9. Privacy

The adapter MUST minimize disclosure.

A Tilden resolution response derived from iTRS MUST expose only information required to establish the authorized communication path. It MUST NOT expose user-registration data, disability status, registration records, provider-internal identifiers, or other non-routing information merely because the underlying systems contain it.

Capability metadata remains endpoint capability metadata. It is not a statement about the identity or disability of the subscriber.

## 10. Failure behavior

The adapter SHOULD distinguish at least:

- no authoritative iTRS route found;
- caller not authorized to perform the requested resolution;
- query context insufficient;
- authoritative directory unavailable; and
- authoritative response invalid or unverifiable.

A failure to obtain an authorized iTRS result MUST NOT be silently converted into a guessed iTRS route.

Policy MAY then permit the Tilden resolver to evaluate other route classes, such as PSTN or another explicitly configured federation route.

## 11. Security boundary

The recommended deployment separates public resolution from protected directory access:

```text
Internet
   |
   v
Tilden edge resolver
   |
   | authenticated private request
   v
Tilden iTRS adapter
   |
   | administrator-required controls
   v
TRS Numbering Directory
```

This permits an edge implementation while keeping iTRS credentials, network restrictions, transaction records, and regulated query behavior inside an authorization boundary.

## 12. Relationship to Baudot

Tilden uses the iTRS query result to identify an authoritative route.

Baudot may then consume that route to establish or bridge the actual signaling and media session.

Tilden does not reinterpret the iTRS URI as a new provider identity and does not become the media path.

## 13. References

- 47 C.F.R. § 64.613, Numbering directory for Internet-based TRS users.
- FCC Internet-based TRS Telephone Numbering Services Statement of Work, sections addressing directory access, query interfaces, portability, and URD interaction.
- TILDEN-CORE-001, Programmable Communications Identity.
- TILDEN-CORE-002, Authority and Delegation.
- TILDEN-CORE-003, Resolution Protocol.
