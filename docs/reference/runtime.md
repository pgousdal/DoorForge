# Runtime — ABBS runtime behaviour reference

## Purpose

Document observable behaviour of a running ABBS node that cannot be
determined from static documentation alone. This reference is populated
from live system observation, not from extracted documents.

## Source

Live ABBS node observation (planned M2+).

## Evidence status

[Partial] — Some runtime behaviour can be inferred from documented ARexx
error handling conventions, but no live observation has been performed.

## Scope

- Carrier detection and loss behaviour
- Timeout behaviour and duration
- Node startup and shutdown sequence
- Door invocation and exit observed on-wire
- Console output conventions
- Signal handling (Ctrl-C, disconnect)
- Performance characteristics

## Verified findings from documentation

### Carrier loss behaviour (DF-EVID-013)

From abbsrexx.doc: ALL ARexx commands may return RC=20 if carrier is lost.
The AREXX program must exit immediately. This is the documented contract.
The exact mechanism of carrier detection (hardware signal, byte timeout,
or both) is not described.

### Timeout behaviour (DF-EVID-041)

RC=20 is also returned for "out of time" conditions. This is documented
as equivalent to carrier loss — the door must exit immediately. The
timeout duration is not documented and is likely configured in ABBS
itself.

### Input function blocking (DF-EVID-042)

`GETLINE` and `READCHAR` are blocking input functions. When they return
RC=20, the caller must exit. `MAYGETCHAR` is non-blocking — it returns
RC=1 if no character is available.

### More-prompt behaviour (DF-EVID-043)

ABBS has a "more" prompt system that pauses output every page. The
`MORE` command re-enables it and `NOMORE` disables it temporarily
(until the next `GETLINE`). `OUTIMAGE` may return RC=1 if the user
selected NO on a more prompt.

### Quick mode (DF-EVID-044)

`QUICK` returns RC=1 if quick mode is active (output is batched).
RC=0 if normal mode. RC=5 if no user on node.

### Raw mode (DF-EVID-045)

`RAW` disables ABBS's character parsing so that `READCHAR` returns
control characters. `RAW OFF` re-enables parsing. This is used for
full-screen applications and binary protocols.

## Partial findings

### Shell door security (DF-EVID-007)

Doors.doc warns: "Skjer den noe galt, så havner brukeren i et shell"
(If something goes wrong, the user ends up in a shell). This is a
documented security risk for Shell doors but has not been verified
on a running system. [Partial]

## Unknowns

- What is the actual carrier-loss detection mechanism?
- What is the default timeout duration?
- Does ABBS send any signal or special character on timeout?
- What happens to the node process when a Shell door crashes?
- Are there any watchdog or heartbeat mechanisms?
- What is the startup sequence for a node?
- Can a node be restarted without restarting the entire BBS?

## Runtime verification required

This entire document is a list of runtime verification items. The
highest-priority items are:

1. Measure actual timeout duration
2. Trigger carrier loss and observe door behaviour
3. Verify SHUTDOWN and EJECT ARexx commands
4. Run two nodes simultaneously and observe isolation
5. Test Shell door failure mode (does user actually get a shell?)
6. Verify TIMELEFT return format
7. Verify GETCONSTAT baud values on real connections

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-013 | abbsrexx.doc | Verified | RC=20 forces immediate exit | Carrier/timeout handling |
| DF-EVID-041 | abbsrexx.doc | Verified | RC=20 includes "out of time" | Timeout handling |
| DF-EVID-042 | abbsrexx.doc | Verified | GETLINE/READCHAR block; MAYGETCHAR non-blocking | Input model |
| DF-EVID-043 | abbsrexx.doc | Verified | More-prompt behaviour | Output model |
| DF-EVID-044 | abbsrexx.doc | Verified | Quick mode detection | Output model |
| DF-EVID-045 | abbsrexx.doc | Verified | RAW toggles character parsing | Input model |
| DF-EVID-007 | Doors.doc | Verified | Shell door security risk | Shell adapter |

## Cross-references

- `docs/reference/arexx.md` — ARexx command return codes
- `docs/reference/doors.md` — Shell door security
- `docs/reference/environment.md` — Runtime variable verification
- `docs/spec/session-model.md` — Session fields requiring runtime validation
