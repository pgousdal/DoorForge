# Node model — ABBS node architecture reference

## Purpose

Document the ABBS node model: how nodes are configured, how they isolate
state, how doors are registered per node, and what multi-node implications
exist for adapter design.

## Source

Primary: `Doors/Node0Config`, `Doors/Node0Menu`, `Docs/Doors.doc`
Supporting: `Config/node1.config` (from archive), `Hold/node1/`, `Hold/node2/`

## Evidence status

[Verified] — Node0Config, Node0Menu, and Doors.doc analysed.

## Scope

- Node configuration file format and content
- Door registration per node
- Hold/mail directory structure per node
- Multi-node locking requirements
- Shared-state risks
- Node 0 special role (if any)

## Verified findings

### Per-node configuration files (DF-EVID-004)

Each node has two configuration files inside `abbs:doors/`:
- `Node<N>Menu` — menu text displayed when user opens doors
- `Node<N>Config` — door registration lines

For node 0: `abbs:doors/Node0Config`, `abbs:doors/Node0Menu`
For node 1: `abbs:doors/Node1Config`, `abbs:doors/Node1Menu`

### Node0Config content (DF-EVID-036)

The extracted Node0Config contains:
```
;
; A = Arexx Door
; P = Paragon Door
; S = Shell Door
;
A    abbs:doors/days/days.abbs     ; Days door
```

This confirms:
- Comment lines start with `;`
- Door type is the first non-whitespace character on valid lines
- A space separates type from path (multiple spaces/tabs allowed)
- Comments after `;` are optional

### Node0Menu content (DF-EVID-037)

The extracted Node0Menu contains:
```
1... Days
```

This is a simple menu entry mapping door number 1 to the label "Days".
The format appears to be `<key><separator><label>`. The separator is
three dots (`...`).

### Hold directories (DF-EVID-038)

From the M0 archive inventory, `Hold/node1/` and `Hold/node2/` directories
exist. This confirms per-node hold/mail state, but the internal format
has not been analysed.

### Node identity in ARexx (DF-EVID-039)

The ARexx port naming convention `"ABBS node #<N> port"` confirms that
each node has a distinct ARexx address. The NODENUMBER ARexx command
returns the current node number. This means node identity is explicitly
available to any ARexx door.

### Multi-node isolation model (DF-EVID-040)

From the evidence:
- Each node has its own configuration files
- Each node has its own hold directory
- Each node has its own ARexx port
- Local variables (FullName, NodeNr) are process-scoped, not shared
- ARexx scripts operate in their own interpreter context

This confirms a per-node isolation model where doors on different nodes
do not share memory, ARexx context, or process state. Shared state
(like bulletin files) must be managed through the filesystem.

## Partial findings

### Node 0 role

Node 0 has its own menu and config files but may be a "template" or
"default" node. The documentation does not explicitly describe whether
Node 0 is special or is an ordinary node. [Partial]

### Menu key format

Node0Menu shows `1... Days` but it is unclear whether the key must be
numeric, whether the separator is always `...`, or whether full ANSI
menu formatting is supported. [Partial]

## Unknowns

- What happens when Node0Config or Node0Menu is missing for a given node?
- Can nodes share door configurations?
- Is there a lock mechanism for shared file access?
- What is the Hold directory format?
- Are there per-node security settings?
- How does ABBS handle node 0 differently (if at all)?

## Runtime verification required

- Verify that Node 0 is functional (not just a template)
- Confirm Hold directory format and usage
- Check for lock files or arbitration mechanisms
- Verify that two nodes can run the same door simultaneously

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-004 | Doors.doc | Verified | Per-node config/menu files | Node configuration |
| DF-EVID-036 | Node0Config | Verified | Node0Config content and format | Configuration parser |
| DF-EVID-037 | Node0Menu | Verified | Node0Menu content | Menu system |
| DF-EVID-038 | Archive inventory | Verified | Hold/node1/ and Hold/node2/ exist | State isolation |
| DF-EVID-039 | abbsrexx.doc | Verified | Per-node ARexx port and NODENUMBER | Node identity |
| DF-EVID-040 | Multiple | Verified | Per-node isolation model | Architecture |

## Cross-references

- `docs/reference/doors.md` — Door config and types
- `docs/reference/arexx.md` — ARexx port naming
- `docs/reference/environment.md` — Per-node variables
- `docs/analysis/abbs-3.20.md` — M0 filename evidence
- `docs/architecture.md` — Multi-node design implications
