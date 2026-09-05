# TILDEN-ESIM-002: Carrier eSIM Identity Binding Profile

**Status:** Draft 0.1  
**Category:** Profile  
**Depends on:** TILDEN-CORE-001  
**Updated:** 2026-09-05

## 1. Abstract

This specification defines an optional carrier-backed eSIM binding for a Tilden E.164 identity.

The eSIM is not the Tilden control plane. It is a carrier credential and interoperability edge that allows the same telephone number used by Tilden to participate in services that require an active cellular subscription.

This profile exists to preserve one stable human-facing number across conventional telephony, accessible federation, and platform-native communications.

## 2. Principle

The eSIM profile preserves the core Tilden invariant:

> **NUMBER != NETWORK**

A Tilden number may be represented simultaneously in multiple communications systems. The eSIM adds one legitimate carrier-backed representation; it does not become the source of truth for every route.

## 3. Scope

This profile defines:

- binding a Tilden E.164 subject to a carrier subscription;
- lifecycle states for that binding;
- capability publication rules;
- separation between carrier authority and Tilden authority;
- platform-registration status semantics;
- revocation and recovery requirements.

This profile does not define:

- GSMA Remote SIM Provisioning protocols;
- carrier IMS internals;
- iMessage or FaceTime signaling;
- a FaceTime gateway;
- an iMessage gateway;
- SIP-to-proprietary-platform translation;
- VRS signaling or media transport.

## 4. Terminology

### 4.1 Tilden number

An E.164 number represented by a Tilden subject such as:

```text
tel:+12025550123
```

### 4.2 Carrier binding

The association between the Tilden number and an active carrier subscription whose telephone number is the same E.164 number.

### 4.3 Tilden eSIM

An eSIM profile issued through a legitimate carrier or mobile service provider for the carrier binding.

### 4.4 Native platform registration

A platform-specific registration of the carrier-backed number, such as use of the number by a device messaging or calling service.

Native platform registration is external state and MUST NOT be treated as ownership authority for the Tilden identity.

## 5. Architecture

```text
                    tel:+12025550123
                       Tilden identity
                              |
              +---------------+---------------+
              |                               |
       Tilden control plane            carrier subscription
              |                               |
       resolution object                     eSIM
              |                               |
     +--------+---------+             +-------+--------+
     |        |         |             |       |        |
    SIP      RTT      Baudot         PSTN    SMS   platform-native
     |        |         |                              services
    VRS    text/video federation
```

The Tilden authority controls Tilden routing assertions.

The carrier controls the cellular subscription and eSIM profile.

A platform operator controls registration and behavior inside that platform.

No one authority automatically inherits the privileges of another.

## 6. Binding requirements

A conforming binding MUST satisfy all of the following:

1. the Tilden subject contains an E.164 number;
2. the carrier subscription is legitimately assigned that same number;
3. the eSIM profile is issued through supported carrier mechanisms;
4. Tilden has verified the number-binding event through an authorized provisioning workflow;
5. revocation of the carrier binding can be reflected promptly in Tilden state.

Tilden MUST NOT simulate a carrier subscription, IMS identity, eSIM profile, or platform registration.

## 7. Resolution representation

A carrier binding MAY be represented as a capability in a Tilden Resolution Object.

Example:

```json
{
  "type": "carrier-esim",
  "uri": "tel:+12025550123",
  "priority": 90,
  "media": ["audio", "text"],
  "features": [],
  "metadata": {
    "state": "active"
  }
}
```

The public object SHOULD expose only the minimum information required to describe reachability.

It MUST NOT expose IMSI, ICCID, EID, activation codes, carrier account credentials, eSIM profile secrets, or equivalent identifiers.

## 8. Lifecycle

A Tilden carrier binding MUST have an explicit lifecycle.

Initial states are:

```text
reserved
provisioning
active
suspended
porting
revoked
```

### 8.1 Reserved

The Tilden number exists but no active carrier binding has been established.

### 8.2 Provisioning

Carrier issuance or eSIM installation is in progress.

### 8.3 Active

The carrier has assigned the number and the subscription is usable.

### 8.4 Suspended

The binding remains known but carrier service is temporarily unavailable or intentionally disabled.

### 8.5 Porting

Control of the number is transitioning between carrier arrangements.

### 8.6 Revoked

The binding is no longer valid and MUST NOT be advertised as active.

## 9. Provisioning flow

A reference flow is:

```text
Tilden number allocated
        |
        v
carrier subscription requested
        |
        v
number assigned or ported to subscription
        |
        v
carrier provisions eSIM through GSMA-compatible mechanisms
        |
        v
user installs/enables profile
        |
        v
carrier service becomes active
        |
        v
Tilden marks carrier binding active
        |
        v
optional platform-native number registration
```

Tilden SHOULD treat GSMA Remote SIM Provisioning as an external dependency rather than reimplement it. The consumer eSIM architecture includes the eUICC, Local Profile Assistant, and SM-DP+ roles; deployments SHOULD use supported carrier infrastructure for those functions.

## 10. Secondary-line deployment

A Tilden eSIM SHOULD support use as a secondary line where the device, carrier, and platform permit it.

This enables a subscriber to retain an existing personal or business carrier line while adding a Tilden number as another communications identity.

Tilden MUST NOT require its eSIM line to be the device's primary data line unless a specific carrier dependency makes that necessary.

## 11. Apple interoperability profile

This section is informative except where it constrains Tilden claims.

As of this specification revision, Apple documents that a phone number used with Messages or FaceTime requires an active SIM or eSIM associated with that number. Apple also documents Dual SIM operation in which both phone numbers can participate in FaceTime calls and messaging.

Therefore a legitimate carrier-backed Tilden eSIM can provide the prerequisite cellular number binding for Apple-native registration of the same E.164 number.

Tilden MUST NOT claim that an active eSIM guarantees successful iMessage or FaceTime registration. Platform policy, device state, account state, carrier support, network access, software version, and activation behavior remain controlled outside Tilden.

Tilden MUST NOT infer that successful number registration creates a server-side FaceTime or iMessage API.

## 12. Platform status

Tilden MAY maintain private operational state describing native platform registration.

If exposed through an authorized API, status SHOULD use bounded values such as:

```text
unknown
available
unavailable
user-disabled
```

Public Tilden resolvers SHOULD NOT probe proprietary platforms to determine user registration state unless an authorized, documented mechanism permits it.

A missing platform registration MUST NOT invalidate the carrier binding.

## 13. Routing behavior

The presence of an active carrier binding MUST NOT force all communications over the carrier network.

Example:

```text
incoming identity: +1 202 555 0123

PSTN call      -> carrier/PSTN route
SMS            -> carrier messaging route
SIP            -> Tilden-discovered SIP endpoint
RTT            -> Tilden-discovered RTT endpoint
VRS            -> Tilden-discovered relay endpoint
Baudot         -> Tilden-discovered federation endpoint
FaceTime       -> Apple-controlled native route, if registered
```

Tilden selects only routes it is authorized to resolve. Platform-native sessions remain native to the platform unless that platform provides an authorized interoperability interface.

## 14. Number portability

The stable Tilden identity SHOULD survive a change of carrier where number portability permits it.

A carrier migration SHOULD preserve:

```text
tel:+12025550123
```

while changing the underlying subscription and eSIM profile.

A porting workflow MUST prevent simultaneous conflicting claims of carrier control.

## 15. Revocation

When the carrier binding is terminated, transferred, or compromised:

1. Tilden MUST cease advertising the binding as active;
2. Tilden routing credentials associated solely with the former binding MUST be revoked;
3. replacement eSIM issuance MUST require an authorized recovery workflow;
4. stale public capability data MUST expire promptly;
5. platform-native registrations SHOULD be removed or allowed to expire using supported platform mechanisms.

Revoking a Tilden carrier binding does not by itself revoke unrelated Tilden endpoints unless policy explicitly couples them.

## 16. Security

Deployments MUST account for:

- SIM-swap attacks;
- unauthorized number porting;
- account takeover;
- fraudulent eSIM reprovisioning;
- recovery-channel compromise;
- stale device credentials;
- unauthorized Tilden endpoint registration.

High-impact operations SHOULD require phishing-resistant authentication where practical.

High-impact operations include:

- replacement eSIM issuance;
- number porting;
- changing recovery credentials;
- changing the authoritative resolver;
- adding a privileged endpoint;
- rotating subscriber authorization keys.

Carrier authentication MUST NOT automatically authorize Tilden control-plane changes.

Tilden authentication MUST NOT automatically authorize carrier-account changes.

## 17. Privacy

Tilden SHOULD publish capability, not subscriber infrastructure.

The public resolution layer MUST NOT disclose:

- IMSI;
- ICCID;
- EID;
- eSIM activation code;
- SM-DP+ transaction secrets;
- Apple Account identifiers;
- carrier account credentials;
- private device identifiers.

## 18. Accessibility requirement

The carrier profile is an interoperability mechanism, not a voice-first policy.

A Tilden deployment SHOULD permit the same number to resolve to accessible modalities including:

- direct sign-language video;
- VRS;
- RTT;
- text;
- captioned speech;
- speech-to-text;
- text-to-speech;
- other federated accessible endpoints.

The existence of a conventional cellular subscription MUST NOT make voice the privileged or mandatory modality in Tilden resolution.

## 19. Conformance

An implementation conforms to this profile when it:

1. preserves the Tilden identity independently of the carrier transport;
2. binds only legitimately assigned carrier numbers;
3. uses supported eSIM provisioning infrastructure;
4. publishes no carrier secrets in Tilden resolution;
5. separates carrier, Tilden, and proprietary-platform authority;
6. implements explicit lifecycle and revocation behavior;
7. does not overclaim interoperability that the external platform does not expose.

## 20. Reference statement

The target user experience is:

> A person gives out one telephone number without first deciding whether the conversation will use PSTN, RTT, SIP, VRS, Baudot, native messaging, native video calling, or another compatible communications system.

**One number. Every modality.**

## 21. Informative references

- Apple Support, "Add or remove your phone number in Messages or FaceTime": https://support.apple.com/en-us/108758
- Apple Support, "Using Dual SIM with an eSIM": https://support.apple.com/en-us/109317
- Apple iPhone User Guide, "Set up FaceTime on iPhone": https://support.apple.com/guide/iphone/set-up-facetime-iph40976f340/ios
- GSMA, "eSIM Consumer and IoT Specifications": https://www.gsma.com/solutions-and-impact/technologies/esim/esim-specification/
