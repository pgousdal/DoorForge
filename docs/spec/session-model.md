# Provisional session model

This model is intentionally BBS-neutral and is not yet a frozen public ABI.

## Design constraints

The session model must not assume ABBS-specific field mappings. Adapters
own all BBS-specific behaviour. The model exists to give door authors a
stable interface across BBS platforms.

## Session field review

Every field is classified against M1 evidence (DF-EVID entries).

### node_number

| Attribute | Value |
|---|---|
| Status | **Verified** |
| DF-EVID | DF-EVID-008 (Doors.doc: NodeNr local variable), DF-EVID-039 (abbsrexx: NODENUMBER ARexx command) |
| Rationale | Confirmed from two independent documented sources |
| Recommendation | **Remain as required field.** `unsigned int` type is appropriate. |

### display_name

| Attribute | Value |
|---|---|
| Status | **Verified** |
| DF-EVID | DF-EVID-008 (Doors.doc: FullName local variable), DF-EVID-019 (abbsrexx: USERNAME ARexx command) |
| Rationale | Confirmed from two independent documented sources |
| Recommendation | **Remain as required field.** `const char*` type is appropriate. |

### minutes_remaining

| Attribute | Value |
|---|---|
| Status | **Verified (format partial)** |
| DF-EVID | DF-EVID-034 (abbsrexx: TIMELEFT available in all ABBS versions) |
| Rationale | Command existence is verified. Return format (seconds, minutes, formatted string) is not documented. |
| Recommendation | **Remain as required field.** `unsigned int` is acceptable if the adapter documents its unit convention. The format ambiguity is an adapter concern, not a model concern. |

### is_local

| Attribute | Value |
|---|---|
| Status | **Verified** |
| DF-EVID | DF-EVID-021 (abbsrexx: GETCONSTAT baud=0 means local) |
| Rationale | Confirmed by documentation with explicit zero-baud convention |
| Recommendation | **Remain as required field.** `int` (boolean) type is appropriate. |

### user_id

| Attribute | Value |
|---|---|
| Status | **Unsupported** |
| DF-EVID | None |
| Rationale | No numeric user ID surface exists in any documented ARexx command or local variable. USERNAME returns a display-name string. USERINFO returns statistics but no numeric ID. No equivalent found. |
| Recommendation | **Made optional in M2.1 (`int | None`, default `None`).** The ARexx adapter sets it to `None`. Do not synthesise from USERNAME. Do not invent a hash convention. The field exists for BBS platforms that provide numeric user IDs; ABBS does not. If no evidence emerges by M4 (native Amiga), consider removing from the BBS-neutral model. |

### security_level

| Attribute | Value |
|---|---|
| Status | **Partially Verified (misaligned)** |
| DF-EVID | DF-EVID-019 (abbsrexx: SYSOP and SIGOP return boolean) |
| Rationale | Only boolean privilege checks are documented (SYSOP RC=1, SIGOP RC=1). No numeric security level exists in the evidence. |
| Recommendation | **Made optional in M2.1 (`int | None`, default `None`).** The ARexx adapter does not populate this field because ABBS exposes no numeric level. Verified boolean privilege is captured in the new `is_sysop: bool` field. The numeric field is retained as provisional for other BBS platforms that do provide levels. |

### is_sysop

| Attribute | Value |
|---|---|
| Status | **Verified** |
| DF-EVID | DF-EVID-019 (abbsrexx: SYSOP command returns RC=1 for sysop) |
| Rationale | Boolean sysop check is documented and verifiable. The ARexx SYSOP command returns RC=1 when the user has sysop privileges, RC=0 otherwise. |
| Recommendation | **Added in M2.1 as a required field.** Adapters for ABBS use the SYSOP command. Other BBS platforms may map their own privilege model. |

## Fields not yet in struct but required by model

### terminal capabilities

| Attribute | Value |
|---|---|
| Status | **Verified — not yet in struct** |
| DF-EVID | DF-EVID-020 (abbsrexx: USERSETUP magic number with bit-encoded terminal profile) |
| Rationale | The USERSETUP command returns charset, ANSI flag, colour flag, page length, transfer protocol, FSE, and other preferences |
| Recommendation | **Do not add yet.** Document as planned future addition. A bitmask or capability struct is appropriate. May be added alongside the first adapter when real usage clarifies the minimum necessary fields. |

### connected state

| Attribute | Value |
|---|---|
| Status | **Partial — not yet in struct** |
| DF-EVID | DF-EVID-021 (GETCONSTAT implies connectivity) |
| Rationale | GETCONSTAT returning data implies a connected user. RC=5 from certain commands implies no user. RC=20 means carrier lost. Connected state is implicit in the error-handling flow. |
| Recommendation | **Do not add.** Connected/disconnected is better represented by adapter error handling (RC=20 → carrier loss exit) than a boolean session field. Adding it would encourage polling a property that changes asynchronously, which the evidence does not support. |

### adapter kind

| Attribute | Value |
|---|---|
| Status | **Unsupported** |
| DF-EVID | None |
| Rationale | Not exposed by ABBS. Inferred from door type (A/P/S) in NodeConfig. |
| Recommendation | **Do not add to core session.** Adapter metadata belongs in the adapter configuration, not the session model. |

## Classification summary (updated for M2.1)

| Field | Python type | C type | Evidence | Required? |
|---|---|---|---|---|
| node_number | int | unsigned int | Verified | Required |
| display_name | str | const char\* | Verified | Required |
| minutes_remaining | int | unsigned int | Verified (format TBD) | Required |
| is_local | bool | int | Verified | Required |
| is_sysop | bool | int | Verified | Required |
| user_id | int \| None | long (-1 = unavailable) | Unsupported | Optional |
| security_level | int \| None | long (-1 = unavailable) | Partial (boolean only) | Optional |
| terminal capabilities | — | — | Verified | Future addition |
| connected state | — | — | Partial | Do not add |
| adapter kind | — | — | Unsupported | Do not add |

## Exit reasons vs evidence (updated for M2.1)

| Value | Status | DF-EVID | Recommendation |
|---|---|---|---|
| normal | Partially Verified | DF-EVID-012 (RC=0 convention) | **Remain.** RC=0 exists for ARexx commands. EXIT without argument in DAYS.ABBS implies normal termination. |
| user_quit | Unsupported | None | **Remain as provisional.** Useful BBS-neutral value. May map to a specific RC or user action in the future. |
| timeout | Verified | DF-EVID-041 (out of time → RC=20) | **Remain** for platforms that distinguish timeout from carrier loss. |
| carrier_loss | Verified | DF-EVID-012, DF-EVID-013 (carrier loss → RC=20) | **Remain** for platforms that distinguish carrier loss from timeout. |
| carrier_loss_or_timeout | Verified | DF-EVID-012, DF-EVID-013, DF-EVID-041 | **Added in M2.1.** Used when the adapter cannot distinguish the two (e.g. ABBS RC=20 covers both). |
| bbs_shutdown | Unknown | None | **Remain as provisional.** SHUTDOWN main command exists but no evidence it propagates to doors. |
| adapter_error | Unsupported | None | **Remain as provisional.** Useful for adapter implementations. |
| door_failure | Unknown | None | **Remain as provisional.** RC>0 error convention exists but no specific mapping. |

## Evidence-driven recommendations (updated for M2.1)

1. **`user_id` is now `int | None` (default `None`).** M2.1 corrected the silent `0` default. The ARexx adapter sets it to `None`. Other BBS adapters may provide a value.
2. **`security_level` is now `int | None` (default `None`).** The ARexx adapter does not populate it. Verified boolean privilege is tracked in `is_sysop: bool`.
3. **`is_sysop: bool` was added** in M2.1 as a required field, justified by DF-EVID-019. It captures the verified ABBS SYSOP command result without pretending to be a numeric scale.
4. **`ExitReason.CARRIER_LOSS_OR_TIMEOUT` was added** for adapters that cannot distinguish the two (e.g. ABBS RC=20). The existing `CARRIER_LOSS` and `TIMEOUT` values remain for platforms that can distinguish them.
5. **`ExecuteResult` was added** to preserve the raw RC alongside the semantic ExitReason, so callers can inspect the original return code.
6. **Terminal capabilities should be added in M3**, not now, to avoid speculative API design.
7. **Connected state should not be added** to the session model. Error handling covers this better.
8. **The public API should evolve from verified evidence, not force the evidence to fit.**
