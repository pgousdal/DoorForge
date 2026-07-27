# DoorForge architecture

## Design principle

The core stays BBS-neutral. All BBS-specific behaviour lives behind an adapter
interface. This lets the session model, the public API, and the host test harness
be reused across different BBS platforms without modification.

## Layer diagram

```
 Application (door, game, utility)
        │
        ▼
 DoorForge API
   (provisional C header / Python reference)
        │
        ▼
 Session Model
   (BBS-neutral, dataclass + validation)
        │
        ▼
 Adapter Interface
   (boundary between neutral core and BBS-specific code)
        │
 ┌──────┴────────┐
 │               │
 ▼               ▼
  Host            Future adapters
  (testing)        │
           ┌───────┼────────────────┬────────┐
           │       │                │        │
           ▼       ▼                ▼        ▼
         ARexx   Shell/Paragon    Native    Other BBS
         (type A) (types S/P)     process
```

## Layer responsibilities

### Application

The door, game, or utility that links against DoorForge. It receives a
`Session` and an adapter handle, performs its logic, and returns an exit
reason when done. It never touches BBS-specific details directly.

### DoorForge API

The public contract between the application and the SDK. Currently a
provisional C header (`include/doorforge/doorforge.h`) and a matching
Python reference (`src/doorforge/`). Provides:

- session information (node, user, security, time, local/remote, display name)
- exit reason vocabulary
- validation rules

The API is **not ABI-stable**. It will be frozen only after at least one
real adapter has been verified against original ABBS documentation.

### Session Model

A BBS-neutral representation of a connected user. Fields are deliberately
generic enough to map onto any BBS platform:

- `user_id` — numeric user identifier
- `node_number` — BBS node the user is connected to
- `security_level` — access level or rank
- `minutes_remaining` — remaining time for this session
- `is_local` — true if the user is on a local console
- `display_name` — human-readable name

All current fields are **provisional**. They may be amended, removed, or
renamed as adapter evidence accumulates.

### Adapter Interface

The conceptual boundary between BBS-neutral types and BBS-specific
plumbing. Each adapter maps its BBS's conventions onto the shared
`Session` shape and exit reason vocabulary.

M0 does not define a concrete adapter interface in code. The boundary
exists as documented intent. A formal interface type will be added when
the first non-host adapter is built.

### Host adapter (implemented, M0)

The host adapter is a Python reference that constructs a `Session` from
command-line arguments and runs without any BBS. It exists to:

- validate the session model shapes before adapters are built
- give door authors a test target that works on any OS
- serve as the integration test fixture

Location: `src/doorforge/session.py`, `examples/hello-door/hello_door.py`

Status: **implemented, provisional**.

### Future adapters

| Adapter | Status | Milestone |
|---|---|---|
| ARexx door (type A) | Planned, not started | M2 |
| Shell door (type S) | Planned, not started | M3 |
| Paragon door (type P) | Future | M4 |
| Other BBS platforms | Future | M6+ |

All future adapters are **planned, not started**. No adapter code exists
in the repository. M1.1 confirmed that the primary integration surface is
the ARexx interface — `.ABBS` files ARE ARexx scripts. M2 is therefore
scoped to the ARexx adapter, not a hypothetical "ABBS script" format.

## Why BBS-neutral

If ABBS-specific identifiers, conventions, or field mappings were baked
into the core, every other BBS platform would require a fork or an awkward
compatibility shim. By keeping the core neutral:

- the same session model works for ABBS, TeleGarden, WWiV, Citadel, etc.
- the same host test harness works for all adapters
- the public API can be documented once and mapped per platform
- the adapter boundary is explicit and testable

## Why adapters own BBS-specific behaviour

An adapter is the only component that knows:

- how to invoke a door on that platform (ARexx, Shell script, or Paragon)
- how to call the platform's session commands (NODENUMBER, USERNAME, etc.)
- what the ARexx message-port naming convention is
- what signals mean carrier loss or timeout (RC=20)
- what the user-record layout is
- how to parse local variables or environment variables

This keeps platform-specific knowledge contained and replaceable.
It also means a mistake in one adapter cannot break another.

## Current status

```
┌─────────────────────────────────────────────┐
│ M0 implemented (verified)                   │
│  - archive hash and entry count             │
│  - filename-level integration map           │
│  - automated inventory checks               │
├─────────────────────────────────────────────┤
│ M0 implemented (provisional)                │
│  - Session dataclass fields                 │
│  - ExitReason vocabulary                    │
│  - C header shape                           │
│  - Hello Door CLI interface                 │
├─────────────────────────────────────────────┤
│ M0.1 (complete)                             │
│  - architecture document                    │
│  - ODS relationship document                │
│  - evidence-first M1 plan                   │
│  - roadmap                                  │
├─────────────────────────────────────────────┤
│ M1 (complete)                                │
│  - evidence model and classification        │
│  - research checklist                       │
│  - reference document framework             │
│  - 41 DF-EVID evidence items registered     │
│  - session model validated against evidence │
│  - M2 readiness: 9/10                       │
├─────────────────────────────────────────────┤
│ M1.1 (complete)                              │
│  - public API validation against evidence   │
│  - session field-by-field review            │
│  - ExitReason review                        │
│  - terminal capability analysis             │
│  - M2 re-scoped to ARexx adapter            │
├─────────────────────────────────────────────┤
│ Future (evidence required first)            │
│  - ARexx adapter code (M2)                  │
│  - native process support                   │
│  - ODS capability mapping                   │
│  - frozen public ABI                        │
└─────────────────────────────────────────────┘
```
