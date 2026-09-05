# Tilden specifications

Tilden specifications use stable identifiers.

## Core

- [`TILDEN-CORE-001.md`](TILDEN-CORE-001.md) — identity, discovery, and capability resolution
- [`TILDEN-AUTH-003.md`](TILDEN-AUTH-003.md) — resolver authority, authenticated bootstrap, delegation, transfer, and revocation

## Profiles

- [`TILDEN-ESIM-002.md`](TILDEN-ESIM-002.md) — carrier-backed eSIM identity binding

The core specification defines the resolution model. Authority specifications define who may speak for an identity. Profiles add interoperability behavior without changing the fundamental identity model.

The primary design invariants are:

> **NUMBER != NETWORK**
>
> **ORIGIN != SUBJECT AUTHORITY**
