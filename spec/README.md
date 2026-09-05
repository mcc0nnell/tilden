# Tilden specifications

Tilden specifications use stable identifiers.

## Core

- [`TILDEN-CORE-001.md`](TILDEN-CORE-001.md) — identity, discovery, and capability resolution

## Trust and integrity

- [`TILDEN-AUTH-003.md`](TILDEN-AUTH-003.md) — resolver authority, authenticated bootstrap, delegation, transfer, and revocation
- [`TILDEN-SIGN-004.md`](TILDEN-SIGN-004.md) — Ed25519-signed Resolution Objects, current-authority verification, replay resistance, and cache/federation integrity

## Interoperability profiles

- [`TILDEN-ESIM-002.md`](TILDEN-ESIM-002.md) — carrier-backed eSIM identity binding
- [`TILDEN-BAUDOT-005.md`](TILDEN-BAUDOT-005.md) — Baudot service discovery, transport selection, modality requirements, readiness, and accessibility-safe fallback

The core specification defines the resolution model. Authority specifications define who may speak for an identity. Signature profiles preserve resolution integrity beyond the live resolver connection. Interoperability profiles add external-system behavior without changing the fundamental identity model.

The primary design invariants are:

> **NUMBER != NETWORK**
>
> **ORIGIN != SUBJECT AUTHORITY**
>
> **A VALID SIGNATURE != CURRENT SUBJECT AUTHORITY**
>
> **SERVICE DISCOVERY != TRANSPORT READINESS**
>
> **SIGNALING SUCCESS != USABLE COMMUNICATION**
