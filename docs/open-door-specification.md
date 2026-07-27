# Relationship to OpenDoorSpecification

## Status

**Planning only.** No ODS artifacts have been copied into this repository.
No ODS integration has been implemented.

## What ODS is

OpenDoorSpecification (ODS) is a vendor-neutral specification for BBS door
operations. It defines:

- canonical operations that every door should support
- compatibility profiles for different levels of BBS integration
- adapter contracts that describe how a door and BBS communicate
- capability declarations that let a door advertise what it supports

ODS is the **normative source** for these definitions.

## What DoorForge is

DoorForge is an **implementation** of a toolkit and SDK that helps developers
build doors. It targets Amiga BBS software (starting with ABBS 3.20) and
aims to provide a portable, testable foundation.

## Intended relationship

```
 OpenDoorSpecification (normative)
        │
        │  informs
        ▼
 DoorForge public API
        │
        │  implemented by
        ▼
 DoorForge adapters
        │
        │  target
        ▼
 Specific BBS platforms
```

ODS defines *what* a door should do. DoorForge defines *how* to build one
for a specific platform.

## What DoorForge must not do

1. **Copy ODS definitions.** Canonical operations, compatibility profiles,
   adapter contracts, and capability declarations belong in ODS. DoorForge
   must not duplicate them.

2. **Publish its own canonical operations.** DoorForge may reference ODS
   identifiers but must not redefine them.

3. **Replace ODS as the normative source.** If a conflict arises, ODS takes
   precedence.

## How integration will work (planned, not implemented)

1. DoorForge defines a BBS-neutral session model and adapter interface
   (M0–M2).
2. After the adapter interface stabilises, it is compared to ODS adapter
   contracts (M5).
3. Where DoorForge concepts map onto ODS concepts, the mapping is
   documented.
4. Where gaps exist, either DoorForge or ODS is updated (the normative
   source decides).
5. DoorForge may optionally generate or validate ODS capability
   declarations, but it does not own those definitions.

## Timeline

| Milestone | ODS relevance |
|---|---|
| M0–M0.1 | None. Repository bootstrap and planning. |
| M1 | None. Evidence gathering only. |
| M2–M4 | Adapter development. ODS is consulted but not integrated. |
| M5 | ODS mapping. Compare DoorForge API against ODS contracts. |

## Non-goals

- DoorForge will not become an ODS conformance test suite.
- DoorForge will not replace ODS documentation.
- DoorForge will not embed ODS catalogs or schemas.
- DoorForge will not require ODS knowledge to build a door.
