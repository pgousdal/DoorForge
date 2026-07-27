# DoorForge

DoorForge is an open-source toolkit and SDK for building testable doors and
utilities for Amiga BBS software. The first target is **ABBS 3.20**.

## Milestone status

| Milestone | Status |
|---|---|
| M0 — ABBS archive analysis and project bootstrap | Complete |
| M0.1 — Architecture and M1 planning | Complete |
| M1 — Verified ABBS documentation | Complete |
| M1.1 — Session API validation | Complete |
| M2 — First verified ARexx adapter | Planned |
| M3 — Shell/Paragon adapters | Planned |
| M4 — Native ABBS runtime | Planned |
| M5 — OpenDoorSpecification integration | Planned |
| M6+ — Additional BBS adapters | Future |

## M0 deliverables

- Reproducible inventory of the supplied ABBS 3.20 archive (222 entries)
- Archive identity: `ABBS320_999.lha`, SHA-256 `5e9fd4cbf871a2bbd…`
- Initial ABBS integration map (door, script, ARexx, node, utility surfaces)
- Deliberately provisional session model and C header
- Host-testable Hello Door skeleton
- Regression tests for inventory identity, key surfaces, session validation,
  and Hello Door output
- Explicit M1 research questions

The proprietary ABBS files are **not included** in this repository or release.

## Important scope rule

The M0 public API is deliberately provisional. The exact runtime contract must
be verified from the original ABBS documentation (`Docs/Doors.doc`,
`Docs/abbsrexx.*`, `DAYS.ABBS`, and live ABBS behaviour) before the public C
API is frozen. M1 is dedicated to that evidence-gathering step.

## Repository layout

```text
docs/architecture.md             Layered architecture overview
docs/evidence-model.md           Knowledge classification and traceability
docs/open-door-specification.md  Relationship to OpenDoorSpecification
docs/m1-plan.md                  Evidence-first M1 workflow
docs/research-checklist.md       Extraction and analysis task tracking
docs/reference/                  Structured evidence reference (per surface)
docs/analysis/                   Archive findings and integration map
docs/spec/                       Provisional DoorForge contracts
include/doorforge/               Future public C headers
src/doorforge/                   Host-side reference implementation
examples/hello-door/             First reference door
tools/                           Reproducible archive inspection tools
reference/                       Generated archive inventory only
tests/                           M0 regression tests
```

## Run the checks

```bash
python -m unittest discover -s tests -v
python tools/inspect_lha.py /path/to/ABBS320_999.lha
```

## Roadmap

### M0 — Repository bootstrap (complete)

Archive inventory, integration map, provisional session model, Hello Door,
tests. No ABBS adapter code.

### M0.1 — Architecture and planning (complete)

Architecture document, ODS relationship document, evidence-first M1 plan,
roadmap. Documentation and cleanup only.

### M1 — Verified ABBS documentation (complete)

Extract, index, and analyse the proprietary ABBS documentation from the
archive. Record verified facts, partial findings, and unknowns. No adapter
code. Output is structured evidence in `docs/reference/`.

### M1.1 — Session API validation (complete)

Reviewed every public API element against verified DF-EVID evidence.
Produced field-by-field classifications, ExitReason review, terminal
capability analysis, and connected state analysis. Confirmed the primary
integration surface is ARexx, not a separate ABBS script format.

### M2 — First verified ARexx adapter (next)

Build a host-testable ARexx adapter that constructs a `Session` using
verified ARexx commands (NODENUMBER, USERNAME, TIMELEFT, GETCONSTAT)
and invokes Type A (ARexx) doors via the documented port protocol.
See `docs/reference/` for the full evidence base.

### M3 — Shell/Paragon adapter

Build adapters for Shell (type S) and Paragon (type P) door types.

### M4 — Native ABBS runtime

Native Amiga process adapter, built only after its contract is documented
from extracted evidence and verified against documentation.

### M5 — OpenDoorSpecification integration

Compare the DoorForge adapter interface against ODS adapter contracts.
Map DoorForge concepts onto ODS canonical operations and capability
declarations without duplicating ODS definitions.

### M6+ — Additional BBS adapters

Support for other BBS platforms as the adapter model matures.
