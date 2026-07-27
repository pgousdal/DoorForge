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
| Recommendation | **Remain as provisional field but make optional for M2 adapters.** Do not synthesise from USERNAME. Do not invent a hash convention. The field exists for BBS platforms that provide numeric user IDs; ABBS does not. If no evidence emerges by M4 (native Amiga), consider removing from the BBS-neutral model. |

### security_level

| Attribute | Value |
|---|---|
| Status | **Partially Verified (misaligned)** |
| DF-EVID | DF-EVID-019 (abbsrexx: SYSOP and SIGOP return boolean) |
| Rationale | Only boolean privilege checks are documented (SYSOP RC=1, SIGOP RC=1). No numeric security level exists in the evidence. The current `unsigned int` type misrepresents the actual ABBS security model. |
| Recommendation | **Remain as provisional field.** The numeric type is not incorrect for other BBS platforms, but evidence does not support it for ABBS. Two possible future resolutions: (1) change to an abstract access-level type (enum or bitmask), or (2) keep numeric and have each adapter define its own mapping, documented as partial. For M2, the adapter should set 0 (non-privileged) or 1 (sysop) and document the limitation. Do not invent 0/100 mappings. |

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

## Classification summary

| Field | C type | Evidence | Keep? | Optional? |
|---|---|---|---|---|
| node_number | unsigned int | Verified | Required | No |
| display_name | const char* | Verified | Required | No |
| minutes_remaining | unsigned int | Verified (format TBD) | Required | No |
| is_local | int | Verified | Required | No |
| user_id | unsigned long | Unsupported | Keep provisional | Yes, for M2 |
| security_level | unsigned int | Partial (boolean only) | Keep provisional | No |
| terminal capabilities | (none) | Verified | Future addition | N/A |
| connected state | (none) | Partial | Do not add | N/A |
| adapter kind | (none) | Unsupported | Do not add | N/A |

## Proposed exit reasons vs evidence

| Value | Status | DF-EVID | Recommendation |
|---|---|---|---|
| normal | Partially Verified | DF-EVID-012 (RC=0 convention) | **Remain.** RC=0 exists for ARexx commands. EXIT without argument in DAYS.ABBS implies normal termination. |
| user_quit | Unsupported | None | **Remain as provisional.** Useful BBS-neutral value. May map to a specific RC or user action in the future. |
| timeout | Verified | DF-EVID-041 (out of time → RC=20) | **Remain.** |
| carrier_loss | Verified | DF-EVID-012, DF-EVID-013 (carrier loss → RC=20) | **Remain.** |
| bbs_shutdown | Unknown | None | **Remain as provisional.** SHUTDOWN main command exists but no evidence it propagates to doors. |
| adapter_error | Unsupported | None | **Remain as provisional.** Useful for adapter implementations. |
| door_failure | Unknown | None | **Remain as provisional.** RC>0 error convention exists but no specific mapping. |

## Evidence-driven recommendations

1. **No API changes in M1.1.** The existing API is provisional and not yet frozen. Every unsupported or partial field has a documented mitigation.
2. **`user_id` should be treated as optional** for M2. Adapters for BBS platforms without numeric user IDs should document that they set this field to 0.
3. **`security_level` semantics should be documented** as "adapter-defined privilege level" rather than "numeric rank". The ABBS adapter will use 0/1 for non-sysop/sysop.
4. **Terminal capabilities should be added in M2 or M3**, not now, to avoid speculative API design.
5. **Connected state should not be added** to the session model. Error handling covers this better.
6. **The ExitReason vocabulary should not change.** All 7 values are valid BBS-neutral categories even when evidence only supports a subset. Unreachable values in a given adapter do not cause harm.
7. **The public API should evolve from verified evidence, not force the evidence to fit.**
