# TILDEN-E164-001: U.S. E.164 Authority Bootstrap

Status: Exploratory Draft

## 1. Purpose

This profile explores how a U.S. NANP telephone number can bootstrap into a verifiable Tilden delegation without treating DNS, a resolver host, or a communications application as the source of telephone-number authority.

It is intentionally conservative. Tilden should integrate with the existing numbering and portability ecosystem rather than create a competing allocation system.

## 2. Existing authority layers

The U.S. numbering system already separates several forms of authority that Tilden must not collapse.

At a high level:

```text
FCC numbering authority
        |
        v
NANPA resource administration
        |
        v
service-provider numbering resources
        |
        v
individual telephone-number assignment / service
        |
        +---- portability state ----> U.S. NPAC / LNPA
```

NANPA assigns central-office codes and, where applicable, thousands-blocks to service providers. Those block-level assignments do not by themselves prove the current serving provider for every individual telephone number, especially after portability.

For ported U.S. telephone numbers, the Number Portability Administration Center is the industry portability system. iconectiv currently serves as the U.S. Local Number Portability Administrator.

NPAC access and use are restricted. Tilden MUST NOT assume that arbitrary public resolvers or callers can query NPAC directly.

## 3. Design conclusion

The public Tilden bootstrap SHOULD NOT be:

```text
caller -> public NPAC lookup -> resolver
```

Instead, the initial model should be:

```text
existing numbering / portability authority
              |
              | proves or authorizes current control
              v
      Tilden authority attestation
              |
              v
       public delegation record
              |
              v
       authoritative resolver
```

This preserves the existing restricted numbering systems while allowing a public, verifiable Tilden control plane to exist above them.

## 4. Provider attestation

A communications service provider that is authorized to serve or port a telephone number MAY issue a Tilden authority attestation for that number.

The attestation states, in effect:

> This provider is currently authorized, within the relevant numbering/portability process, to establish Tilden delegation for this telephone number.

An attestation SHOULD contain:

- normalized telephone number;
- attesting provider identifier;
- attestation type;
- issuance time;
- expiration time;
- monotonic sequence or equivalent freshness value;
- subscriber or account authorization reference where appropriate;
- public verification method;
- signature.

The attestation MUST NOT expose proprietary NPAC records or other restricted data merely to prove the result.

## 5. Attestation types

Initial profile candidates include:

### 5.1 `serving-provider`

The attester asserts that it is the current provider serving the telephone number and is permitted to authorize the Tilden delegation.

### 5.2 `port-activation`

The attester asserts that a completed portability event has transferred current service authority to the attesting provider.

### 5.3 `direct-number-assignment`

The attester asserts that the number is currently assigned through numbering resources under its control and has not been superseded by a portability state known to the provider.

These names describe Tilden proof semantics, not new regulatory categories.

## 6. Subscriber authorization

Provider authority and subscriber authorization are distinct.

A provider may be able to prove that it serves a number, while the subscriber determines where that number should resolve within Tilden.

Therefore a complete delegation may require both:

```text
provider authority
       +
subscriber authorization
       |
       v
Tilden delegation
```

Subscriber authorization MAY use mechanisms such as:

- authenticated provider account action;
- explicit service-order action;
- cryptographic enrollment;
- an application flow backed by provider authentication;
- another profile-defined proof.

A one-time SMS or voice challenge by itself SHOULD NOT be treated as strong proof of durable numbering authority, because successful receipt proves reachability at a moment in time rather than the complete authority chain.

## 7. Public discovery directory

Because NPAC is not a general public directory, Tilden needs a separate public discovery surface.

A Tilden E.164 directory MAY publish only the minimum delegation material required to discover and verify a resolver:

```json
{
  "identifier": "tel:+12025550142",
  "resolver": "https://resolver.example/tilden/v1/resolve",
  "authorityAttestation": "urn:tilden:attestation:...",
  "verificationMethod": "did:web:provider.example#tilden-authority-1",
  "sequence": 42,
  "expiresAt": "2026-09-06T21:00:00Z",
  "proof": { "...": "..." }
}
```

The directory does not need to reveal the subscriber name, account data, NPAC record, service address, or endpoint inventory.

## 8. Directory governance

This draft does not require a single global Tilden directory.

Possible deployment models include:

- multiple federated directories with common validation rules;
- a national directory operated by a neutral administrator;
- provider-published records discovered through a common bootstrap;
- a DNS-based index containing only delegation pointers;
- a hybrid model.

Whatever model is chosen, directory operators MUST NOT become durable owners of the telephone numbers they index.

## 9. Portability event

A port should invalidate the previous provider's ability to mint fresh Tilden authority for the number.

Conceptually:

```text
before port
-----------
provider A attestation -> delegation A -> resolver A

port activates
------------
number remains tel:+12025550142
provider A authority becomes stale
provider B gains current serving authority

post-port
---------
provider B attestation -> delegation B -> resolver B
```

A relying party that has observed delegation B MUST reject an older delegation A solely because A's signature remains cryptographically valid.

Freshness and authority sequence are therefore part of Tilden security, not just caching optimization.

## 10. Non-ported numbers

For numbers that have not been ported, block-level NANPA assignment can help identify the original resource holder but is not necessarily sufficient public proof of the subscriber's current Tilden authorization.

The serving provider remains the natural bridge between numbering-resource administration and individual subscriber delegation.

## 11. Why NANPA alone is insufficient

NANPA administers numbering resources such as NPA-NXX codes and thousands-blocks. An individual number may later be ported to another provider while retaining the same digits.

Therefore:

```text
NPA-NXX-X holder != guaranteed current serving provider for every TN
```

Tilden MUST account for portability before treating block ownership as current per-number authority.

## 12. Why NPAC alone is insufficient

NPAC provides critical portability state, but its data is not an unrestricted public namespace. Authorized use is limited to defined telecommunications purposes and qualified users.

Therefore Tilden should consume an attested result from authorized ecosystem participants rather than require public redistribution of restricted NPAC data.

## 13. Neutrality

The E.164 bootstrap SHOULD preserve provider neutrality.

No carrier, VRS provider, edge host, application store, operating-system vendor, or Tilden resolver should gain permanent control merely because it currently serves the user.

The design target is:

> existing numbering authority establishes who may delegate; Tilden makes that delegation portable and verifiable.

## 14. Failure and dispute handling

A production profile will need procedures for:

- conflicting provider attestations;
- delayed portability propagation;
- number reassignment after service termination;
- account takeover;
- provider key compromise;
- stale directories;
- subscriber disputes;
- disconnected and aging numbers;
- reclaimed numbering resources.

Resolution during a dispute SHOULD fail conservatively rather than silently accept an older route that may now belong to the wrong subscriber.

## 15. Privacy

The public bootstrap SHOULD reveal no more than is necessary to establish resolver authority.

In particular, it SHOULD NOT expose:

- subscriber name;
- disability or accessibility status;
- VRS registration status;
- endpoint presence;
- billing relationships;
- account identifiers;
- raw portability records.

## 16. Reference implementation path

A safe initial proof of concept can emulate the authority system without claiming production numbering authority:

```text
fixture authority service
        |
        v
signed provider-attestation fixture
        |
        v
Tilden delegation directory
        |
        v
Cloudflare Worker resolver
        |
        v
signed resolution object
```

The fixture layer can later be replaced by an authorized numbering/portability integration without changing the resolver protocol.

## 17. Informative sources

- FCC, Third Local Number Portability Administrator Selection Process, DA 24-104: https://docs.fcc.gov/public/attachments/DA-24-104A1.pdf
- U.S. NPAC / iconectiv overview: https://www.numberportability.com/
- U.S. NPAC general FAQ: https://www.numberportability.com/support/faq/general
- NANPA, CO Codes / Thousands-Blocks: https://www.nanpa.com/numbering/co-codesthousands-blocks

## 18. Open questions

- Which entities may issue production Tilden provider attestations?
- Does the FCC/NANC ecosystem need to recognize a Tilden directory role?
- Can existing LNPA-authorized interfaces support the necessary verification without disclosing restricted NPAC data?
- Should a Tilden authority service qualify as a Provider of Telecom-Related Services for particular deployments?
- What is the correct handoff when a number is disconnected and later reassigned?
- What maximum propagation interval is acceptable after a port?
- How should direct-numbering VoIP providers and resellers participate?
- What changes, if any, are required for iTRS numbering and direct-video identifiers?
