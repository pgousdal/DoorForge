# M2 / M2.1 readiness report

## Prepared from M1 + M1.1 evidence

Generated after analysing: Doors.doc, DAYS.ABBS, DAYS.DOC, Node0Config,
Node0Menu, abbsrexx.doc, abbsrexx.guide, and validating the public API
against all evidence.

## What M2 delivered

A **host-testable ARexx adapter core and client abstraction**:

1. `ArexxClient` ABC with `call()` / `close()` and typed `ArexxResult`
2. `MockArexxClient` for deterministic host-side testing
3. `ArexxAdapter` that:
   - Populates a `Session` using five ARexx commands (NODENUMBER, USERNAME,
     TIMELEFT, GETCONSTAT, SYSOP)
   - Executes a door script and maps the RC to an `ExitReason`
   - Returns an `ExecuteResult` preserving the raw RC

**No real Amiga ARexx transport exists.** The implementation is host-tested
only.

## What M2.1 corrected

| Issue | Before | After |
|---|---|---|
| `user_id` | Set to 0 (silent placeholder) | `int \| None` (default `None`); adapter sets `None` |
| `security_level` | 0/1 mapped from SYSOP RC | `int \| None` (default `None`); adapter sets `None` |
| Boolean privilege | Merged into invented numeric scale | New `is_sysop: bool` field (DF-EVID-019) |
| RC=20 exit | Arbitrarily picked `carrier_loss` | `CARRIER_LOSS_OR_TIMEOUT` — honest combined value |
| Adapter return type | Bare `ExitReason` | `ExecuteResult` with raw RC preserved |
| C header | `unsigned long` with no sentinel | `long` with `-1` sentinel for unavailable fields |
| Version | Claimed 1.0.0 | Corrected to 0.3.0 (pre-1.0, no stabilised ABI) |

## Verified foundations

- `.ABBS` = ARexx script format (DF-EVID-025) ✓
- Port naming: `"ABBS node #<N> port"` (DF-EVID-011) ✓
- Session.node_number via NODENUMBER (DF-EVID-008, DF-EVID-039) ✓
- Session.display_name via USERNAME (DF-EVID-008, DF-EVID-019) ✓
- Session.minutes_remaining via TIMELEFT (DF-EVID-034) ✓
- Session.is_local via GETCONSTAT baud=0 (DF-EVID-021) ✓
- Session.is_sysop via SYSOP RC=1 (DF-EVID-019) ✓
- I/O: writetext/outimage for output, getline/readchar for input (DF-EVID-027) ✓
- Exit: RC=0 = OK, RC=20 = carrier/timeout (indistinguishable), EXIT to terminate (DF-EVID-012, DF-EVID-028) ✓
- Node isolation: per-node config, ARexx port, hold directory (DF-EVID-040) ✓

## Important considerations

| # | Issue | DF-EVID | Mitigation |
|---|---|---|---|
| C1 | TIMELEFT return format unspecified | DF-EVID-034 | Assume seconds; document assumption explicitly in `_parse_timeleft()`; raw value preserved in call_log |
| C2 | user_id unsupported in evidence | — | `None`; do not synthesise |
| C3 | security_level boolean-only | DF-EVID-019 | `is_sysop` captures the verified boolean; numeric `security_level` is `None` |
| C4 | No host-side ARexx interpreter | — | Mock ARexx commands in Python for host testing; real transport deferred to M4 |
| C5 | Terminal capabilities not in Session struct | DF-EVID-020 | Deferred to M3 |
| C6 | Connected state not in Session struct | DF-EVID-021 | Error handling covers this |
| C7 | RC=20 conflates carrier_loss and timeout | DF-EVID-012, DF-EVID-041 | `CARRIER_LOSS_OR_TIMEOUT` + raw RC preserved |

## Session field readiness (post-M2.1)

| Field | M2 ready? | How the adapter populates it |
|---|---|---|
| node_number | YES | NODENUMBER ARexx call |
| display_name | YES | USERNAME ARexx call |
| minutes_remaining | YES (unit assumed seconds) | TIMELEFT ARexx call; explicit conversion contract in `_parse_timeleft()` |
| is_local | YES | GETCONSTAT baud=0 → local; non-zero → remote |
| is_sysop | YES | SYSOP RC=1 → True |
| user_id | N/A (None) | Evidence does not support numeric user IDs |
| security_level | N/A (None) | Evidence exposes only boolean sysop |

## ExitReason readiness (post-M2.1)

| Value | Status | How determined |
|---|---|---|
| normal | RC=0 | EXIT RC=0 convention |
| carrier_loss_or_timeout | RC=20 | ABBS RC=20 covers both; raw_rc=20 preserved |
| adapter_error | RC=5 | No active user on node |
| door_failure | Other RC | Any RC not 0, 5, or 20 |

Values `carrier_loss`, `timeout`, `user_quit`, and `bbs_shutdown` exist in
the ExitReason vocabulary but are not produced by the ARexx adapter. They
remain available for other platforms or adapters.

## Remaining limitations

- No native Amiga ARexx transport (M4 milestone)
- TIMELEFT unit assumption (seconds) unverified — documented as adapter contract
- Shell and Paragon adapter not built (M3 milestone)
- Terminal capabilities not exposed (deferred to M3)
- ODS conformance not evaluated (M5 milestone)
- No runtime ABBS validation (blocked by M4)
