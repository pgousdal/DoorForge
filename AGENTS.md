# AGENTS.md

## Project purpose

DoorForge provides a small, testable SDK and toolchain for Amiga BBS doors.
ABBS 3.20 is the first target.

## Non-negotiable rules

1. Do not commit or redistribute proprietary ABBS binaries, documentation, keys,
   configuration, or extracted archive contents.
2. Keep archive-derived evidence in inventories, hashes, filenames, sizes, and
   original analysis—not copied proprietary text.
3. Treat the ABBS runtime protocol as provisional until verified from original
   documentation and a live system.
4. Keep core APIs BBS-neutral; ABBS-specific behavior belongs in an adapter.
5. Every Amiga-facing feature needs a host-testable equivalent where practical.
6. Avoid dependencies that are unavailable on classic AmigaOS.
7. Prefer ANSI C for the stable SDK ABI. ARexx and ABBS scripts are valid and
   desirable integration layers.
8. Never silently reinterpret carrier loss, timeout, node identity, or user
   identity. These are explicit session events.
9. Run the full test suite before declaring a milestone complete.
10. Document all assumptions and separate them from verified facts.

## M0 constraints

M0 is analysis and scaffolding only. It must not claim that a native ABBS door
ABI has been reverse-engineered or implemented.
