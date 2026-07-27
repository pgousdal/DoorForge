# ABBS 3.20 archive analysis

## Source identity

- Archive: `ABBS320_999.lha`
- Format: Amiga LHA, primarily `-lh5-`
- Size: 751581 bytes
- SHA-256: `5e9fd4cbf871a2bbd4579a3f9b35a0cd2187676cab8886b16adbfe8b038380e4`
- Parsed entries: 222

The inventory was generated directly from LHA headers. It does not require
decompressing proprietary files and is therefore suitable for inclusion in the
DoorForge repository.

## High-value findings

### 1. ABBS has an explicit door subsystem

The archive contains:

- `ABBS/Docs/Doors.doc`
- `ABBS/Doors/Node0Config`
- `ABBS/Doors/Node0Menu`
- `ABBS/Doors/DAYS/DAYS.ABBS`
- `ABBS/Doors/DAYS/DAYS.DOC`

This is direct evidence that ABBS 3.20 supports configurable doors and includes
at least one sample or bundled door named DAYS.

### 2. `.ABBS` is a first-class executable/script surface

Examples include:

- `sys/Download.abbs`
- `sys/LoginScript.abbs`
- `sys/LogoutScript.abbs`
- `sys/Newuser.abbs`
- `sys/Questionnaire.ABBS`
- `sys/login/Clock.abbs`
- `Doors/DAYS/DAYS.ABBS`

This strongly suggests that DoorForge should not begin by assuming that every
door is an independently linked native executable. ABBS script integration is
a primary candidate for the first supported adapter.

### 3. ARexx integration is substantial

The archive contains:

- `Docs/abbsrexx.doc`
- `Docs/abbsrexx.guide`

Together they occupy over 24 KiB uncompressed. This is strong evidence that
ABBS exposes a meaningful ARexx interface. DoorForge should model ARexx as a
supported bridge, not as an optional afterthought.

### 4. Node-local operation matters

Evidence includes:

- `Config/node1.config`
- `Doors/Node0Config`
- `Doors/Node0Menu`
- `Hold/node1/`
- `Hold/node2/`
- multiple node-oriented text menus

The SDK must therefore carry an explicit node identity and must avoid unsafe
shared-state writes. Multi-node locking belongs in the design from the start.

### 5. ABBS provides external utilities and command-oriented integration

The archive has documented utilities including `AddFile`, `AddMsg`,
`Broadcast`, `SysopAvail`, `UserEditor`, `ConfigBBS`, and `ConfigNode`.
This suggests that a useful DoorForge adapter may combine:

1. ABBS scripts;
2. ARexx commands;
3. command-line utilities;
4. native processes only where required.

## What M0 verifies

Verified from archive metadata:

- the filenames listed above exist;
- the archive contains 222 entries;
- door, ARexx, script, node, and utility surfaces are all represented;
- a bundled `DAYS` door exists;
- the archive contains documentation specifically named for doors and ARexx.

## What M0 does not verify

Not yet verified because the compressed document bodies have not been included
or quoted:

- exact door launch arguments;
- message-port names;
- ARexx command names and return conventions;
- environment variables;
- carrier-loss behavior;
- timeout semantics;
- user-record layout;
- whether `DAYS.ABBS` is interpreted, compiled, or launched through another
  component;
- native binary ABI or required compiler conventions.

## Recommended adapter order

After M1 evidence is collected, the implementation order should be:

1. `host` adapter for deterministic tests (M0 — complete);
2. `abbs-script` adapter based on verified `.ABBS` behavior (planned M2);
3. `abbs-arexx` bridge for session and BBS commands (planned M3);
4. native Amiga process adapter only after its contract is documented (planned M4).

## M1 evidence checklist (from `docs/m1-plan.md`)

- Extract and read `Docs/Doors.doc`.
- Extract and read both `Docs/abbsrexx` documents.
- Inspect `Doors/DAYS/DAYS.ABBS` and `DAYS.DOC`.
- Inspect `Doors/Node0Config` and `Node0Menu`.

## M2 prerequisites (after M1 evidence)

- Trace one bundled door invocation on a running ABBS node.
- Record inputs, outputs, return codes, node behavior, timeouts, and disconnects.
- Write a minimal, manually verified Hello Door.
- Freeze only the smallest API supported by evidence.
