# Changelog

## 0.3.0 — M2.1 (evidence-safe API hardening)

- Changed `Session.user_id` from `int` to `int | None` (default `None`).
  No ABBS evidence supports numeric user IDs (DF-EVID-035).  Unavailable
  values are now explicitly `None` instead of silently `0`.
- Added `Session.is_sysop: bool` (required field) for the verified ABBS
  boolean privilege check (DF-EVID-019).  The AREXX SYSOP command returns
  RC=1 for sysop, RC=0 otherwise.
- Changed `Session.security_level` from `int` to `int | None` (default
  `None`).  ABBS exposes only boolean sysop; no numeric level exists in
  evidence.  The field is retained as optional for other BBS platforms.
- Added `ExitReason.CARRIER_LOSS_OR_TIMEOUT` to honestly represent
  RC=20, which ABBS uses for both carrier loss and timeout (DF-EVID-012,
  DF-EVID-041).  The adapter no longer fabricates a distinction by
  picking one arbitrarily.
- Added `ExecuteResult` dataclass wrapping `ExitReason` plus the raw RC,
  so callers can inspect the original return code alongside the semantic
  reason.
- Changed `ArexxAdapter.execute()` return type from `ExitReason` to
  `ExecuteResult`.
- Updated provisional C header (`doorforge.h`) with sentinel-based
  unavailable fields (`long user_id = -1`, `long security_level = -1`),
  new `is_sysop` flag, and `DF_EXIT_CARRIER_LOSS_OR_TIMEOUT` enum value.
- Added 16 regression tests (47 total): unavailable user_id, unavailable
  security_level, is_sysop True/False, CARRIER_LOSS_OR_TIMEOUT, raw_rc
  preservation, Session optional defaults, None validation.
- Updated `session.py`, `adapter.py`, `__init__.py` to export
  `ExecuteResult`.
- Version corrected from 1.0.0 (premature) to 0.3.0.  DoorForge has
  no stabilised public ABI, no native Amiga transport, no ODS
  conformance, and no runtime ABBS validation.

## 0.2.1 — M1.1 (session API validation)

- Reviewed every Session field against verified DF-EVID evidence.
- Classified 6 current fields: 4 Verified, 1 Unsupported, 1 Partial.
- Reviewed 7 ExitReason values: 2 Verified, 1 Partial, 2 Unsupported, 2 Unknown.
- Analysed terminal capability evidence (READUSERSETUP); deferred to M3.
- Analysed connected state evidence; recommended not to add to session model.
- Re-scoped M2 from "ABBS script adapter" to "ARexx adapter".
- Updated architecture.md adapter list and status table.
- Updated m2-readiness.md with post-review findings.
- Updated AGENTS.md with evidence-first design principles.

## 0.2.0 — M1 (evidence collection)

- Extracted and analysed 7 primary ABBS documents from the archive.
- Registered 41 DF-EVID evidence items across 6 reference documents.
- Verified: door subsystem model (3 door types, per-node config, local variables).
- Verified: ARexx interface (40+ commands, port naming, RC conventions, USERSETUP).
- Verified: .ABBS = ARexx script format (confirmed from DAYS.ABBS source).
- Verified: node model (per-node isolation, config files, ARexx ports).
- Verified: carrier loss and timeout both produce RC=20 (forced exit).
- Partial: session field mapping (5 of 10 fields verified; user_id unsupported).
- Partial: TIMELEFT format unconfirmed, security level boolean-only.
- Partial: exit reason vocabulary partially supported (2 of 7 values verified).
- Updated session-model.md with evidence validation table.
- Updated glossary with verified ABBS terminology.
- Updated evidence-model.md with registered evidence summary.

## 0.0.1 — M0.1

- Added layered architecture document.
- Added OpenDoorSpecification relationship document.
- Revised M1 plan to evidence-first workflow (no adapter code in M1).
- Added roadmap with milestone sequence M0–M6+.
- Removed stale M0-TEST-RESULTS.txt.
- Added M0-TEST-RESULTS.txt to .gitignore.

## 0.0.0 — M0

- Added reproducible ABBS 3.20 archive inventory.
- Documented door, ABBS script, ARexx, utility, and node-related evidence.
- Added provisional BBS-neutral session model.
- Added host-only Hello Door.
- Added M0 regression tests.
- Explicitly excluded proprietary ABBS content.
