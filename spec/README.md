# Tilden specifications

Tilden specifications use stable identifiers.

## Core

- `TILDEN-CORE-001.md` — programmable communications identity and routing model
- `TILDEN-CORE-002.md` — authority, delegation, resolver discovery, portability, caching, and revocation
- `TILDEN-CORE-003.md` — HTTPS resolution protocol

## Profiles

- `TILDEN-E164-001.md` — exploratory U.S. E.164 authority bootstrap
- `TILDEN-ITRS-001.md` — authorized TRS Numbering Directory query profile
- `TILDEN-CAP-001.md` — endpoint capability vocabulary and privacy semantics

## Architectural rules

> Resolve first. Connect second.

> The number owns the route. The route does not own the number.

For identifiers already governed by a specialized authoritative routing system, a Tilden profile SHOULD adapt the authoritative result rather than recreate that authority. `TILDEN-ITRS-001` applies that rule to the FCC TRS Numbering Directory.
