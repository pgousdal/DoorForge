# Native Amiga ARexx transport

## Overview

The native transport consists of two components:

1. **`arexx-cli`** — a small ANSI C executable that sends ARexx commands
   to an ABBS node port and prints the result to stdout.
2. **`AmigaArexxClient`** — a Python `ArexxClient` implementation that
   invokes `arexx-cli` as a subprocess and parses its output.

## Architecture

```
DoorForge Python API
     │
     ▼
ArexxClient (ABC)
     │
     ├── MockArexxClient  (host testing)
     │
     └── AmigaArexxClient  (native Amiga transport)
              │
              ▼  subprocess
         arexx-cli  (ANSI C, AmigaOS)
              │
              ▼  ARexx message port
         "ABBS node #<N> port"
```

## Building `arexx-cli`

### Prerequisites

- AmigaOS 2.04+ (minimum for ARexx support via `rexxsyslib.library` V33)
- VBCC + vlink (recommended) or m68k-amigaos-gcc
- NDK SDK includes (`proto/rexxsyslib.h`, `rexx/rxslib.h`, `rexx/storage.h`)

### Build command

```shell
# GCC (cross-compiler found at /opt/amiga)
make

# Manually
m68k-amigaos-gcc -O2 -I/path/to/ndk-include -o arexx-cli arexx_cli.c -lamiga

# VBCC (not yet tested with the corrected API)
# vc -c99 -lamiga +larexx -o arexx-cli arexx_cli.c
```

### Output

`arexx-cli` — AmigaOS executable (no `.exe` suffix needed).

## Usage

```shell
# Send NODENUMBER to node 1
arexx-cli 1 NODENUMBER
# Output:
# RC:0
# RESULT:1

# Send USERNAME to node 2
arexx-cli 2 USERNAME
# Output:
# RC:0
# RESULT:Alice
```

## Output format

| Line | Meaning |
|---|---|
| `RC:<number>` | ARexx return code (0 = OK, 20 = carrier/timeout) |
| `RESULT:<text>` | Command result string (may be empty), C-escaped |
| `ERROR:<text>` | Transport error (port not found, library missing, etc.) |

The RESULT and ERROR values are C-escaped: `\\` → `\`, `\n` → newline,
`\r` → carriage return.  The Python parser unescapes them automatically.

Exit code: 0 on success, 1 on transport error.

## Port naming

The port name is constructed from verified evidence (DF-EVID-011):
`"ABBS node #<N> port"` where `<N>` is the node number. No other format
is used. This is the exact format documented in abbsrexx.doc.

## Timeouts

`arexx-cli` uses Exec `PutMsg()` / `WaitPort()` / `GetMsg()` for
ARexx message passing. `WaitPort()` blocks indefinitely if ABBS
never replies — there is no built-in ARexx timeout. The Python
`AmigaArexxClient` enforces a configurable timeout on the subprocess
level (default 30 seconds), which kills the helper if ABBS hangs.

## Limitations

- Only tested with ABBS 3.20
- No support for non-ABBS ARexx ports
- Not validated on a live ABBS system (requires runtime testing)
- `WaitPort()` blocks indefinitely if ABBS never replies — subprocess
  timeout is the only safeguard
- Uses standard ARexx `rm_Result2` argstring format via
  `LengthArgstring()`; binary data in results is preserved
  but not explicitly tested
