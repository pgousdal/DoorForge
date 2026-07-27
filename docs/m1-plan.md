# M1 plan — verified ABBS documentation

## Objective

Obtain verified documentary evidence from the ABBS 3.20 archive *before* any
adapter code is written. M1 produces no code adapters. It produces indexed,
analysed, and categorised evidence that later milestones (M2+) depend on.

## Tracking

- **Research checklist**: `docs/research-checklist.md` — tracks each
  extraction task with per-document sub-tasks and status.
- **Evidence model**: `docs/evidence-model.md` — classification scheme,
  traceability convention, and handling rules.
- **Reference documents**: `docs/reference/` — one document per integration
  surface with placeholder sections for verified, partial, unknown, and
  runtime evidence.

## Workflow

```
Acquire archive (already done — M0)
       │
       ▼
Extract documents to temporary directory     ← outside repository
       │
       ▼
Convert proprietary format to searchable text
       │
       ▼
Index facts: environment variables, call conventions, exit codes, ports
       │
       ▼
Record verified facts as structured analysis  ← into repository
       │
       ▼
Identify unknowns
       │
       ▼
Identify items that require live ABBS runtime verification
       │
       ▼
Publish evidence summary → M2 begins
```

## Required primary sources

The following files must be extracted and analysed:

1. `Docs/Doors.doc` — door subsystem documentation
2. `Doors/DAYS/DAYS.ABBS` — bundled example door
3. `Doors/DAYS/DAYS.DOC` — DAYS door documentation
4. `Doors/Node0Config` — node door configuration
5. `Doors/Node0Menu` — door menu definition

Secondary (supporting, not blocking):

6. `Docs/abbsrexx.doc`
7. `Docs/abbsrexx.guide`

## Questions M1 must answer

For each primary source, the analysis must identify:

- Environment variables set before a door is launched
- How node identity, user identity, security level, remaining time are conveyed
- Stdin/stdout/stderr conventions
- Exit codes and signalling conventions
- ARexx message-port names (if documented)
- Whether `.ABBS` files are interpreted, compiled, or launched indirectly
- What happens on carrier loss and timeout
- User-record layout (if relevant to session construction)
- Native binary ABI conventions (if documented)

## Entry criteria

- All five primary source files exist and are intact in the archive
  (verified by M0 inventory)
- Extraction environment is ready (Amiga LHA extractor or emulator)
- Temporary working directory outside the DoorForge repository

## Exit criteria

- Structured analysis notes committed as `docs/analysis/abbs-documentation.md`
- Verified facts, partial findings, and unknowns are explicitly separated
- Each session model field is validated, amended, or marked unverifiable
  against extracted evidence
- Items requiring runtime verification are listed
- All M0 tests continue to pass
- No proprietary text, file bodies, or verbatim quotes are committed
- No adapter code is written

## Classification scheme

Every extracted document element is classified as one of:

| Label | Meaning |
|---|---|
| **Verified** | Confirmed by explicit statement in ABBS documentation |
| **Partial** | Implied but not directly stated; needs cross-reference |
| **Unknown** | No mention found in any extracted source |
| **Runtime** | Requires live ABBS node to confirm |

## What happens after M1

The evidence summary feeds directly into M2 design:

- If `.ABBS` is a simple script format → M2 builds an ABBS script adapter
- If `.ABBS` requires ARexx for invocation → M2 may be an ARexx bridge
- If documentation describes a native binary ABI → M2 may revise the order

No choice is locked in before M1 evidence is collected.

## Outside scope

- Any adapter implementation (M2+)
- Reverse engineering of binary formats
- Decompilation of Amiga executables
- Live ABBS trace (requires a running ABBS system; listed as a runtime item)
- OpenDoorSpecification integration (M5)
- Freezing the C header ABI
- Adding fields to `Session` or `DFSessionInfo`

## Proprietary material handling

- Archive extraction happens outside the repository
- No extracted file body enters the repository
- Findings are recorded as structured analysis (tables, lists, descriptions)
- No verbatim quotes from proprietary documentation

## Risk register

| Risk | Mitigation |
|---|---|
| `.ABBS` is bytecode/compiled, not text | Check first bytes after extraction; report format without reverse-engineering |
| Archive files are corrupt or unreadable | Confirm integrity via M0 inventory before extraction |
| Extracted documentation is incomplete or absent | Cross-reference with ARexx docs and file structure |
| Documentation does not describe environment variables | Report negative finding; deferred to runtime verification |
| Door invocation path differs from documented behaviour | Document as requiring runtime confirmation |

## Non-goals

- Do not freeze the ABI.
- Do not add API surface without evidence.
- Do not reverse-engineer binary formats.
- Do not commit extracted file bodies.
- Do not promise an Amiga runtime component.
- Do not write any adapter code.
