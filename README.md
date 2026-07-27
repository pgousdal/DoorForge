# DoorForge

DoorForge is an open-source toolkit and SDK for building testable doors and
utilities for Amiga BBS software.

## M0 status

This repository is the **M0 ABBS archive analysis and project bootstrap**.
The first target is **ABBS 3.20**.

M0 contains:

- a reproducible inventory of the supplied ABBS archive;
- an initial ABBS integration map;
- a deliberately provisional adapter contract;
- a host-testable Hello Door skeleton;
- tests for the archive inventory and repository structure;
- explicit M1 research questions.

The proprietary ABBS files are **not included** in this repository or release.
The analysis was produced from a user-supplied archive with this identity:

- Filename: `ABBS320_999.lha`
- Size: `751581` bytes
- SHA-256: `5e9fd4cbf871a2bbd4579a3f9b35a0cd2187676cab8886b16adbfe8b038380e4`
- Entries discovered: `222`

## Important scope rule

M0 does not pretend that the binary door protocol is fully known. The supplied
archive clearly exposes several integration surfaces, but the exact runtime
contract must be verified from `Docs/Doors.doc`, `Docs/abbsrexx.*`, the
`DAYS.ABBS` sample, and live ABBS behavior before the public C API is frozen.

## Repository layout

```text
docs/analysis/       Archive findings and evidence
docs/spec/           Provisional DoorForge contracts
include/doorforge/   Future public C headers
src/doorforge/       Host-side reference implementation
examples/hello-door/ First reference door
tools/               Reproducible archive inspection tools
reference/           Generated archive inventory only
tests/               M0 regression tests
```

## Run the checks

```bash
python -m unittest discover -s tests -v
python tools/inspect_lha.py /path/to/ABBS320_999.lha
```

## M1 exit direction

M1 should begin only after the ABBS door documentation and sample door have
been extracted and converted to searchable text. M1 then implements one verified
integration path end-to-end, preferably an ABBS script/ARexx bridge before a
native binary ABI is promised.
