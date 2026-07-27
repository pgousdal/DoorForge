# Evidence model

## Purpose

Define how ABBS knowledge enters the DoorForge repository and how its
reliability is communicated to future implementors.

## Knowledge classification

Every documented fact is assigned one of four labels:

| Class | Tag | Meaning |
|---|---|---|
| Verified | `[Verified]` | Confirmed by explicit statement in primary ABBS documentation |
| Partial | `[Partial]` | Implied, incomplete, or inferred from cross-referencing multiple sources |
| Unknown | `[Unknown]` | No mention found in any extracted source |
| Runtime | `[Runtime]` | Cannot be determined from documentation alone; requires live ABBS node |

## How facts enter the repository

1. A source document from the ABBS archive is extracted to a temporary
   directory outside the repository.
2. Relevant sections are read and analysed. No verbatim text is copied.
3. The analyst writes a structured summary (tables, lists, descriptions)
   into the appropriate `docs/reference/` document.
4. Every claim is tagged with its classification.
5. The source archive path and file modification date (from LHA header) are
   recorded for provenance.

## How assumptions are marked

Assumptions — statements that are plausible but unconfirmed — are explicitly
prefixed with `[Assumption]` in the text and coloured `Partial`.

If an assumption later becomes `Verified` or `Runtime` it is relabelled. If
disproven, it is struck through with a note explaining why.

## Runtime observations vs documentation

Documentation describes intended behaviour. Runtime observations describe
actual behaviour. They may differ. The distinction is maintained:

| Source | Tag | Precedence |
|---|---|---|
| ABBS documentation | `[Verified]` | Design intent |
| Live node observation | `[Runtime]` | Actual behaviour; overrides documentation if conflict is confirmed |

Conflicts are recorded explicitly in the affected reference document with
both sources quoted indirectly (paraphrased, not verbatim).

## Conflicting evidence

When two sources disagree:

1. Both claims are recorded with their respective sources.
2. The conflict is flagged with `[Conflict: source A vs source B]`.
3. If one source is clearly more authoritative (e.g., `Doors.doc` vs a
   comment in a config file), that is noted.
4. The conflict is resolved only when a third source or live observation
   confirms one side. Until then, the item remains `[Partial]`.

## Uncertain information

If the evidence is ambiguous:

- Use `[Partial]` and describe the ambiguity.
- Phrase findings as specific questions: "Unclear whether X or Y."
- Do not guess. An explicit `[Unknown]` is better than a plausible guess
  that later turns out wrong.

## Traceability convention

Every distinct piece of evidence that may affect implementation is assigned
a unique identifier.

### Format

```
DF-EVID-NNN
```

`NNN` is a zero-padded sequence number (001, 002, …). IDs are never reused.
If an item is superseded, the old ID is marked `[Superseded by DF-EVID-MMM]`.

### Registration

Evidence items are registered in two places:

1. **Primary registry**: the reference document that owns the evidence.
   Each `docs/reference/*.md` document may define its own evidence table.
2. **Cross-reference**: when an evidence item in one document affects a
   component documented elsewhere, the target document mentions the ID.

### Registered evidence

As of M1 completion, **41 DF-EVID entries** are registered across the
`docs/reference/` documents. See each document's Evidence Registry
section for the full list. Summary:

| Range | Topic | Primary reference |
|---|---|---|
| DF-EVID-001–003 | Reserved (pre-registration) | — |
| DF-EVID-004–010 | Door subsystem | `docs/reference/doors.md` |
| DF-EVID-011–024 | ARexx interface | `docs/reference/arexx.md` |
| DF-EVID-025–033 | ABBS script surface | `docs/reference/scripts.md` |
| DF-EVID-034–035 | Environment/local variables | `docs/reference/environment.md` |
| DF-EVID-036–040 | Node model | `docs/reference/node-model.md` |
| DF-EVID-041–045 | Runtime behaviour | `docs/reference/runtime.md` |

## Prohibited practices

- Do not copy verbatim text from proprietary documentation.
- Do not invent field mappings that are not present in the evidence.
- Do not upgrade `[Partial]` or `[Unknown]` to `[Verified]` without source.
- Do not delete conflicting evidence; preserve both sides with annotation.
- Do not remove an `[Unknown]` tag until the gap is explicitly filled.
