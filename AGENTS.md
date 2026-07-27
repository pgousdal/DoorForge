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

## Evidence-handling principles

11. **Unknown is safer than a fabricated value.** If evidence does not support
    a field or behaviour, leave it unknown rather than inventing a plausible
    mapping.
12. **Partial evidence must remain partial.** Do not upgrade partial findings
    to verified facts without new primary source confirmation.
13. **Runtime assumptions are not verified facts.** Behaviour observed on a
    live system must be tagged `[Runtime]` and kept distinct from documented
    intent.
14. **Adapters expose gaps, they do not hide them.** When evidence is
    insufficient to populate a session field, the adapter should document the
    gap rather than invent a value.
15. **The public API evolves from verified evidence, not the reverse.** Do
    not force evidence to fit an existing API shape. Amend the API when
    evidence contradicts it.
16. **Do not add speculative API surface.** Every field, enum value, or
    function must be justified by existing or anticipated evidence from at
    least one BBS platform.

## M0 constraints

M0 is analysis and scaffolding only. It must not claim that a native ABBS door
ABI has been reverse-engineered or implemented.
