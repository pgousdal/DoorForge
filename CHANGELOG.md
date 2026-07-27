# Changelog

## 0.2.1 - M1.1 (session API validation)

- Reviewed every Session field against verified DF-EVID evidence.
- Classified 6 current fields: 4 Verified, 1 Unsupported, 1 Partial.
- Reviewed 7 ExitReason values: 2 Verified, 1 Partial, 2 Unsupported, 2 Unknown.
- Analysed terminal capability evidence (READUSERSETUP); deferred to M3.
- Analysed connected state evidence; recommended not to add to session model.
- Re-scoped M2 from "ABBS script adapter" to "ARexx adapter".
- Updated architecture.md adapter list and status table.
- Updated m2-readiness.md with post-review findings.
- Updated AGENTS.md with evidence-first design principles.

## 0.2.0 - M1 (evidence collection)

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

## 0.0.1 - M0.1

- Added layered architecture document.
- Added OpenDoorSpecification relationship document.
- Revised M1 plan to evidence-first workflow (no adapter code in M1).
- Added roadmap with milestone sequence M0–M6+.
- Removed stale M0-TEST-RESULTS.txt.
- Added M0-TEST-RESULTS.txt to .gitignore.

## 0.0.0 - M0

- Added reproducible ABBS 3.20 archive inventory.
- Documented door, ABBS script, ARexx, utility, and node-related evidence.
- Added provisional BBS-neutral session model.
- Added host-only Hello Door.
- Added M0 regression tests.
- Explicitly excluded proprietary ABBS content.
