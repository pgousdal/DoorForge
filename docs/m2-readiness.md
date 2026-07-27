# M2 readiness report

## Prepared from M1 + M1.1 evidence

Generated after analysing: Doors.doc, DAYS.ABBS, DAYS.DOC, Node0Config,
Node0Menu, abbsrexx.doc, abbsrexx.guide, and validating the public API
against all evidence.

## Adapter target (revised)

M2 targets a **host-testable ARexx adapter** that:
1. Connects to (or simulates) an ABBS node ARexx port
2. Populates a `Session` using ARexx commands
3. Invokes a Type A (ARexx) door script
4. Manages I/O via ARexx write/read commands
5. Returns an `ExitReason` on termination

**Why ARexx, not "ABBS script":** M1 evidence confirmed that `.ABBS`
files ARE ARexx scripts (DF-EVID-025). There is no separate "ABBS script
format" — only ARexx. The original M2 name was misleading and has been
corrected.

## Verified foundations

The following are confirmed by documented evidence and do not require
further research before M2:

- `.ABBS` = ARexx script format (DF-EVID-025) ✓
- Port naming: `"ABBS node #<N> port"` (DF-EVID-011) ✓
- Session.node_number via NODENUMBER (DF-EVID-008, DF-EVID-039) ✓
- Session.display_name via USERNAME (DF-EVID-008, DF-EVID-019) ✓
- Session.minutes_remaining via TIMELEFT (DF-EVID-034) ✓
- Session.is_local via GETCONSTAT baud=0 (DF-EVID-021) ✓
- I/O: writetext/outimage for output, getline/readchar for input (DF-EVID-027) ✓
- Exit: RC=0 = OK, RC=20 = carrier/timeout, EXIT to terminate (DF-EVID-012, DF-EVID-028) ✓
- Node isolation: per-node config, ARexx port, hold directory (DF-EVID-040) ✓

## Critical blockers

**None.** No item prevents M2 from building a working adapter.

## Important considerations

| # | Issue | DF-EVID | Mitigation |
|---|---|---|---|
| C1 | TIMELEFT return format unspecified | DF-EVID-034 | Assume seconds; document assumption; verify during M2 validation |
| C2 | user_id unsupported in evidence | — | Mark as optional; set to 0 for ABBS; do not synthesise |
| C3 | security_level boolean-only | DF-EVID-019 | Set 0/1 (non-sysop/sysop); document as adapter's best effort |
| C4 | No host-side ARexx interpreter | — | Mock ARexx commands in Python for host testing; use subprocess for real Amiga |
| C5 | Terminal capabilities not in Session struct | DF-EVID-020 | Do not block M2; defer to API extension in M3 |
| C6 | Connected state not in Session struct | DF-EVID-021 | Do not add; error handling covers this |

## Session field readiness (post-M1.1 review)

| Field | M2 ready? | How the adapter populates it |
|---|---|---|
| node_number | YES | NODENUMBER ARexx call |
| display_name | YES | USERNAME ARexx call |
| minutes_remaining | YES (unit TBD) | TIMELEFT ARexx call; document unit assumption |
| is_local | YES | GETCONSTAT baud=0 → local; non-zero → remote |
| user_id | OPTIONAL | Set to 0. Evidence does not support numeric user IDs. Field remains provisional. |
| security_level | PARTIAL | SYSOP RC=1 → 1, else 0. Document as boolean-only. |

## ExitReason readiness

| Value | M2 ready? | How determined |
|---|---|---|
| normal | PARTIAL | ARexx EXIT without RC=20; RC=0 convention |
| carrier_loss | YES | RC=20 from any input command |
| timeout | YES | RC=20 from any input command (same RC, cannot distinguish) |
| user_quit | PARTIAL | No direct evidence; may be detectable through application protocol |
| bbs_shutdown | NO | Not detectable from within a door |
| adapter_error | YES | ARexx RC != 0 and != 20 |
| door_failure | YES | Script crash or unexpected EXIT |

Note: carrier_loss and timeout share RC=20 and cannot be distinguished
from available evidence. Adapter may report both as `carrier_loss` or
`timeout` and document the limitation.

## Readiness score

**9/10 — ready for M2.**

- Critical blockers: 0
- Important considerations: 6 (all have documented mitigations; none block)
- Session fields: 4 verified, 1 optional, 1 partial with documented mapping
- Exit reasons: 5 of 7 reachable; 2 deferred

M2 should start with an ARexx adapter prototype using the NODENUMBER,
USERNAME, TIMELEFT, WRITETEXT, GETLINE, and READCHAR commands. A host-side
mock of these ARexx commands will enable deterministic testing without a
live Amiga.
