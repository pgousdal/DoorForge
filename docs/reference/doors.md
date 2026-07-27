# Doors — ABBS door subsystem reference

## Purpose

Document the ABBS door subsystem: how doors are launched, configured, and
how they communicate with the BBS. This is the primary source for the
door adapter contract.

## Source

Primary: `Docs/Doors.doc` (1994-01-02), `Doors/DAYS/DAYS.DOC`
Supporting: `Doors/Node0Config`, `Doors/Node0Menu`

## Evidence status

[Verified] — Doors.doc analysed. DAYS.DOC analysed.

## Scope

- Door launch arguments and environment
- Door entry and exit conventions
- Configuration file format (Node0Config, Node0Menu)
- Return codes and exit signalling
- Relationship to ABBS scripts and native executables
- Sample door behaviour (DAYS)

## Verified findings

### Door directory layout (DF-EVID-004)

The ABBS door directory is `abbs:doors`. Each node requires two files inside
it: `Node<N>Menu` and `Node<N>Config` where `<N>` is the node number.

For node 1: `abbs:doors/Node1Menu`, `abbs:doors/Node1Config`.

### NodeConfig format (DF-EVID-005)

NodeConfig uses lines of the form:

```
<type> <path> ; <comment>
```

Where:
- `<type>` is one of `A` (ARexx door), `P` (Paragon door), `S` (Shell door)
- `<path>` is the file path (no spaces or tabs allowed in path)
- `; <comment>` is optional
- Spaces or tabs before the type are ignored
- At least one space or tab must separate type from path
- Pure comment lines (starting with `;`) are ignored for door numbering
- Valid lines are counted 1-based to determine door number

Example from Node0Config (node 0):
```
A    abbs:doors/days/days.abbs     ; Days door
```

### Door types (DF-EVID-006)

Three door types are available:

| Type | Name | Behaviour |
|---|---|---|
| `A` | ARexx door | Launched as an ARexx script via the ABBS ARexx interface |
| `P` | Paragon door | Launched as a Paragon-format door |
| `S` | Shell door | Launched via an AmigaDOS shell script |

### Shell door script structure (DF-EVID-007)

Shell doors use an AmigaDOS script that typically:

1. Changes to the door directory (`cd doors:xbj`)
2. Sets `failat 2147483647` (max error ignore)
3. Sets stack size (`stack 10000`)
4. Sets `path` to find the ARexx interpreter
5. Optionally sends an ARexx command to update node status text
6. Launches the native door binary
7. Ends with `EndCli` (critical — prevents shell escape)

Example from Doors.doc:
```amigados
cd doors:xbj
failat 2147483647
stack 10000
path sys:rexxc
rx "Address 'ABBS node #`get Nodenr` port' 'SETSTATUSTEXT ''Playing Black Jack'''"
xbj -u "`get fullname`"
Endcli
```

Risk: if the shell script fails, the user may be dropped into an AmigaDOS
shell, which is a security hazard.

### Local variables available to doors (DF-EVID-008)

Two local variables are documented:

| Variable | Content |
|---|---|
| `FullName` | The user's logon name |
| `NodeNr` | The node number the user is on |

These are retrieved using the AmigaDOS `C:get` command:
```
`get fullname`
`get Nodenr`
```

The variables are set as local (process-scoped) variables, not environment
variables. Shell doors use `C:get` to read them. ARexx doors use the
USERNAME and NODENUMBER ARexx commands instead.

### Paragon door type (DF-EVID-009)

The `P` type launches a door as a "Paragon door". The exact Paragon
protocol is not documented in Doors.doc. This is a different integration
surface from ARexx and Shell types.

## Partial findings

### Door numbering (DF-EVID-010)

Doors are numbered by counting valid configuration lines from 1. A
"valid line" is any non-empty line that matches the format. Comment-only
lines are not counted. This is straightforward for simple configs but
may be ambiguous if blank lines or malformed lines exist. [Partial]

### Menu file format

Node0Menu contains `1... Days` — suggesting the format is
`<door number><separator><label>`. The exact parsing rules (separator
characters, maximum length) are not documented in Doors.doc. [Partial]

## Unknowns

- Are there additional local variables beyond `FullName` and `NodeNr`?
- Are environment variables also set for native doors, or only local vars?
- What is the native binary ABI for Paragon and Shell doors?
- What is the exact exit-code convention for native doors?
- What signals carrier loss or timeout to a Shell door?
- Are there global environment variables set before any door type runs?
- What is the maximum number of doors per node?
- Can the NodeConfig path use AmigaDOS variable indirection beyond `abbs:`?

## Runtime verification required

- Confirm that only `FullName` and `NodeNr` are set (no other local vars)
- Verify Shell door exit code handling
- Observe actual Paragon door behaviour
- Confirm that carrier loss produces a signal or stdin close for Shell doors

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-004 | Doors.doc | Verified | Door directory layout per node | NodeConfig |
| DF-EVID-005 | Doors.doc | Verified | NodeConfig file format with type/path/comment | Adapter interface |
| DF-EVID-006 | Doors.doc | Verified | Three door types: ARexx, Paragon, Shell | Adapter dispatch |
| DF-EVID-007 | Doors.doc | Verified | Shell door script structure and risks | Shell adapter |
| DF-EVID-008 | Doors.doc | Verified | Local variables FullName and NodeNr | Session fields |
| DF-EVID-009 | Doors.doc | Verified | Paragon door type exists | Paragon adapter |
| DF-EVID-010 | Doors.doc | Partial | Door counting from valid lines | Door numbering |

## Cross-references

- `docs/reference/environment.md` — Local variables vs environment
- `docs/reference/scripts.md` — ARexx script format (type A)
- `docs/reference/node-model.md` — Per-node config files
- `docs/reference/arexx.md` — ARexx commands for doors
- `docs/spec/session-model.md` — Session fields to validate
