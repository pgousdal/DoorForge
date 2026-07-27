# Scripts — ABBS script surface reference

## Purpose

Document the `.ABBS` script surface: file format, execution model,
environment interface, and lifecycle. This is the primary source for the
first ABBS script adapter.

## Source

Primary: `Doors/DAYS/DAYS.ABBS`
Supporting: `Docs/Doors.doc`, `Docs/abbsrexx.doc`

## Evidence status

[Verified] — DAYS.ABBS analysed. ARexx script format confirmed.

## Scope

- File format (text script, bytecode, or compiled)
- Shebang or interpreter directive
- Environment variables available to scripts
- Stdin, stdout, stderr conventions
- Exit codes and signalling
- Security context (which user does the script run as?)
- Script lifecycle (when is it invoked, when does it terminate?)

## Verified findings

### File format (DF-EVID-025)

`.ABBS` files are **ARexx scripts** — text files written in the ARexx
language. DAYS.ABBS has no shebang line; it is invoked via the ABBS
ARexx interpreter directly.

The file uses standard ARexx syntax:
- `/* ... */` block comments
- `options results` at top to enable return values
- `name = RESULT` captures return values
- `CALL subroutine()` calls subroutines
- `select/when/otherwise/end` for conditionals
- `IF ... THEN ... ELSE ... END` for branching
- `DO ... END` for blocks
- `EXIT` terminates the script
- `RETURN` returns from a subroutine
- `PARSE ARG textLine` parses arguments
- String concatenation with `||`
- Variables are local by default

### ARexx commands used in DAYS.ABBS (DF-EVID-026)

The DAYS door uses the following ARexx commands:

| Command | Usage |
|---|---|
| `writetext` | Send text to user |
| `outimage` | Flush output buffer with newline |
| `breakoutimage` | Flush output buffer without newline |
| `getline <n>` | Read a line (max n chars); RC=20 on timeout |
| `readchar` | Read a single character; RC=20 on timeout |
| `DATE(S)` | System date in YYYYMMDD format |
| `DATE(C)` | System date in days since epoch |
| `DATE(W)` | Current weekday name |
| `DATE(N)` | Current date string |
| `CALL open(name, path, mode)` | Open a file |
| `CALL writeln(name, text)` | Write line to file |
| `CALL writech(name, text)` | Write characters to file |
| `CALL close(name)` | Close a file |
| `exists(path)` | Check if file exists |
| `UPPER(str)` | Convert to uppercase |
| `strip(str, option, char)` | Strip characters |
| `substr(str, pos, len)` | Extract substring |
| `abs(n)` | Absolute value |

### Input/output conventions (DF-EVID-027)

- `writetext` + `breakoutimage` → write text without trailing newline
- `writetext` + `outimage` → write text with trailing newline
- `getline <n>` → read a line from the user, up to n characters
- `readchar` → read a single character from the user
- `RC = 20` on any input command means carrier loss or timeout; script
  must `EXIT` immediately

### Exit conventions (DF-EVID-028)

- `EXIT` terminates the script and returns control to ABBS
- No explicit exit code is set in DAYS.ABBS — it always calls `EXIT`
  without an argument
- `IF RC > 0 THEN EXIT` is used to abort on errors
- RC is set by ARexx commands; if not explicitly set, RC from the last
  command persists
- There is no evidence of a specific exit-code convention for doors

### File I/O (DF-EVID-029)

ARexx scripts can read and write files on the Amiga filesystem:
- `call open('handle', path, 'W')` — open for write
- `call open('handle', path, 'A')` — open for append
- `call writeln('handle', text)` — write line
- `call writech('handle', text)` — write characters
- `call close('handle')` — close
- `exists(path)` — check file existence

DAYS.ABBS writes user birthday statistics to a bulletin file
(`ABBS:bulletins/News1` by default).

### ANSI escape support (DF-EVID-030)

ARexx scripts can send ANSI escape codes directly via `writetext`:
- `c` — reset terminal
- `[0m` — reset attributes
- `[33m` — yellow text
- `[32m` — green text
- `[31m` — red text
- `[36m` — cyan text
- `[37m` — white text
- `[44m` — blue background
- `[1 p` — set paging mode (proprietary)

### Script configuration pattern (DF-EVID-031)

DAYS.ABBS uses in-script configuration via ARexx variables at the top:

```rexx
SYSOP = 'Dr. Ice'            /* Sysop name */
BULL = 'ABBS:bulletins/News1' /* Bulletin file */
```

This is a pattern where the door author edits the script directly to set
configuration values. There is no separate config file for the script.

### Node interaction pattern (DF-EVID-032)

The DAYS.ABBS script does NOT use NODENUMBER or USERNAME — it is an
ARexx type-A door, so ABBS sets the FullName and NodeNr local variables
before invoking the script. The script uses these implicitly through
the ARexx environment.

However, DAYS.ABBS uses `UPPER(UNAME)` where `UNAME = RESULT` — but
`RESULT` is never set by a prior command in the listing, which suggests
USERNAME is called implicitly when the script is launched as an ARexx
door, or there is an implicit variable `UNAME`/`USERNAME` that is
pre-populated. This is a partial finding.

## Partial findings

### Implicit USERNAME pre-population (DF-EVID-033)

DAYS.ABBS uses `USERNAME; UNAME = RESULT` but the listing suggests
`UNAME` may be implicitly available. The exact mechanism is unclear.
May be that ABBS calls USERNAME on the script's behalf before
execution, or that the comment block separator `/*` before this line
is actually a comment and the real variable is set differently. [Partial]

### No explicit door numbering in script

The script does not read its door number. It relies on ABBS to have
matched the config entry. This is consistent with the ARexx door
type where ABBS handles dispatch. [Partial]

## Unknowns

- Are there `.ABBS` files that are not ARexx scripts?
- How does ABBS select the ARexx interpreter for `.ABBS` files?
- Are there any environment variables set before `.ABBS` execution?
- What is the exact mechanism for populating UNAME/USERNAME?
- Can `.ABBS` scripts receive command-line arguments directly?
- What happens if an `.ABBS` script has a syntax error?

## Runtime verification required

- Confirm that USERNAME is implicitly called or pre-populated
- Verify the ARexx interpreter path used by ABBS
- Check RC values after `EXIT` without argument
- Verify that stdin/stdout is connected to the user's terminal

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-025 | DAYS.ABBS | Verified | .ABBS is ARexx script format | Script adapter |
| DF-EVID-026 | DAYS.ABBS | Verified | ARexx commands used by DAYS | ARexx adapter |
| DF-EVID-027 | DAYS.ABBS | Verified | I/O conventions (writetext, getline, readchar) | I/O model |
| DF-EVID-028 | DAYS.ABBS | Verified | EXIT terminates script; RC from last command | ExitReason |
| DF-EVID-029 | DAYS.ABBS | Verified | File I/O via open/writeln/close | File system access |
| DF-EVID-030 | DAYS.ABBS | Verified | ANSI escape code support | Terminal output |
| DF-EVID-031 | DAYS.ABBS | Verified | In-script configuration variables | Config pattern |
| DF-EVID-032 | DAYS.ABBS | Verified | Script does not call NODENUMBER/USERNAME | Session context |
| DF-EVID-033 | DAYS.ABBS | Partial | USERNAME may be pre-populated by ABBS | Session fields |

## Cross-references

- `docs/reference/doors.md` — ARexx door type (type A)
- `docs/reference/arexx.md` — ARexx command reference
- `docs/reference/environment.md` — Local variables vs environment
- `docs/reference/runtime.md` — Script execution behaviour
- `docs/spec/session-model.md` — Session fields to validate
