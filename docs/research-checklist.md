# M1 research checklist

## Workflow reference

See `docs/m1-plan.md` for the full evidence workflow and extraction rules.
This document tracks progress against individual extraction tasks.

## Archive evidence extraction

All tasks target the ABBS 3.20 archive (`ABBS320_999.lha`, SHA-256
`5e9fd4cbf871a2bbd4579a3f9b35a0cd2187676cab8886b16adbfe8b038380e4`).

Extraction happens outside the repository. Only analysis notes are committed.

## Task status

| # | Source document | Primary reference | Status |
|---|---|---|---|
| 1 | `Docs/Doors.doc` | `docs/reference/doors.md` | Not Started |
| 2 | `Doors/DAYS/DAYS.ABBS` | `docs/reference/scripts.md` | Not Started |
| 3 | `Doors/DAYS/DAYS.DOC` | `docs/reference/doors.md` | Not Started |
| 4 | `Doors/Node0Config` | `docs/reference/node-model.md` | Not Started |
| 5 | `Doors/Node0Menu` | `docs/reference/node-model.md` | Not Started |
| 6 | `Docs/abbsrexx.doc` | `docs/reference/arexx.md` | Not Started |
| 7 | `Docs/abbsrexx.guide` | `docs/reference/arexx.md` | Not Started |

## Status definitions

| Status | Meaning |
|---|---|
| Not Started | Extraction or analysis not yet begun |
| In Progress | Document extracted; analysis underway |
| Verified | Analysis complete and committed |
| Deferred | Postponed to later milestone; documented reason |

## Per-document extraction checklist

### Task 1 — Docs/Doors.doc

- [ ] Extract to temporary directory
- [ ] Convert Amiga DOC format to plain text
- [ ] Record file size and modification date
- [ ] Identify launch argument conventions
- [ ] Identify environment variable descriptions
- [ ] Identify exit code conventions
- [ ] Identify any native ABI documentation
- [ ] Identify carrier loss and timeout handling
- [ ] Identify user record layout if described
- [ ] Commit structured notes to `docs/reference/doors.md`

### Task 2 — Doors/DAYS/DAYS.ABBS

- [ ] Extract to temporary directory
- [ ] Determine file format (text script, bytecode, or compiled)
- [ ] If text, record relevant structure and conventions
- [ ] If binary, note format without reverse engineering
- [ ] Identify shebang or interpreter directive if present
- [ ] Commit structured notes to `docs/reference/scripts.md`

### Task 3 — Doors/DAYS/DAYS.DOC

- [ ] Extract to temporary directory
- [ ] Convert Amiga DOC format to plain text
- [ ] Record documented behaviour of DAYS door
- [ ] Identify configuration file format
- [ ] Identify integration requirements
- [ ] Commit structured notes to `docs/reference/doors.md`

### Task 4 — Doors/Node0Config

- [ ] Extract to temporary directory
- [ ] Record configuration key names and value formats
- [ ] Identify how doors reference config values
- [ ] Commit structured notes to `docs/reference/node-model.md`

### Task 5 — Doors/Node0Menu

- [ ] Extract to temporary directory
- [ ] Record menu structure and syntax
- [ ] Identify how door entries are specified
- [ ] Commit structured notes to `docs/reference/node-model.md`

### Task 6 — Docs/abbsrexx.doc

- [ ] Extract to temporary directory
- [ ] Convert Amiga DOC format to plain text
- [ ] Identify ARexx command names and arguments
- [ ] Identify message-port naming conventions
- [ ] Identify return value conventions
- [ ] Identify security or access controls
- [ ] Commit structured notes to `docs/reference/arexx.md`

### Task 7 — Docs/abbsrexx.guide

- [ ] Extract to temporary directory
- [ ] Convert Amiga GUIDE format to plain text
- [ ] Cross-reference with abbsrexx.doc for completeness
- [ ] Commit any additional findings to `docs/reference/arexx.md`

## Cross-cutting tasks

- [ ] Identify all environment variables across all sources
- [ ] Validate each provisional `Session` field against evidence
- [ ] List items requiring live ABBS runtime verification
- [ ] Update `docs/reference/glossary.md` with verified terminology
- [ ] Register all verified findings as DF-EVID entries in reference docs
