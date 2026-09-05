# Tilden Cloudflare Worker reference resolver

This is a deliberately small executable reference implementation of the Tilden control-plane boundary.

It demonstrates:

```text
POST resolution request
        |
        v
Cloudflare Worker
        |
        +-- validate identifier
        +-- evaluate capability compatibility
        +-- select candidate routes
        +-- bind response to authority sequence
        +-- apply bounded freshness
        +-- sign demo response
        |
        v
Tilden resolution object
```

It does **not** terminate SIP, WebRTC, RTT, VRS, or media.

That is the point.

## Run locally

```bash
npm install
npx wrangler secret put TILDEN_SIGNING_SECRET
npm run dev
```

Use any non-production secret for local testing.

The checked-in fixture includes one example identifier:

```text
tel:+12025550142
```

## Resolve it

```bash
curl -sS http://localhost:8787/tilden/v1/resolve \
  -H 'content-type: application/json' \
  -H 'accept: application/tilden+json' \
  --data '{
    "version": "0.1",
    "identifier": "tel:+12025550142",
    "requestId": "demo-1",
    "capabilities": {
      "media": ["video", "text"],
      "protocols": ["sip", "webrtc"],
      "features": ["asl"]
    }
  }'
```

The fixture will prefer the SIP route because it has the lower routing priority and satisfies all requested capabilities.

## Configure routes

`TILDEN_ROUTES` is a JSON-encoded environment variable in this minimal example. A production implementation would normally use a durable configuration store, database, or federation-aware authority service.

The current fixture looks conceptually like:

```json
{
  "tel:+12025550142": {
    "delegationSequence": 17,
    "verificationMethod": "urn:tilden:demo:hmac-sha256",
    "endpoints": [
      {
        "id": "primary-video",
        "uri": "sip:alice@example.net",
        "protocol": "sip",
        "priority": 10,
        "capabilities": ["video", "asl", "rtt"]
      }
    ]
  }
}
```

## Important: demo signing only

The Worker uses HMAC-SHA-256 only to make the reference flow executable without prematurely selecting Tilden's production signature suite.

HMAC uses shared secret material and therefore is **not** the intended public federation verification model.

A production Tilden profile should use the signature and verification mechanism selected by the standards work, with independently verifiable public keys and defined canonicalization.

Do not treat `TildenDemoHmacSha256` as a registered Tilden proof type.

## Why a Worker fits

The resolver operation is ordinary control-plane computation:

1. receive a normalized identifier and optional capability context;
2. load authoritative routing policy;
3. select appropriate candidate endpoints;
4. return a signed, short-lived result.

That is naturally deployable at the edge.

Cloudflare is only one implementation target. The same resolver contract can run on another edge platform, a conventional application server, a carrier service, or a federated communications provider.

## Next step

Replace the checked-in route fixture with two independent components:

```text
Tilden delegation directory
        |
        v
resolver authority validation
        |
        v
route store
```

Then make a Baudot gateway consume the Worker response and establish the selected SIP/WebRTC/RTT path.
