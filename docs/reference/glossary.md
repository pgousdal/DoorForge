# Glossary

## Terms

### Adapter

A component that maps a specific BBS platform's conventions onto the
DoorForge BBS-neutral Session model and ExitReason vocabulary.

### ARexx (verified)

The Amiga REXX implementation (ARexx). ABBS exposes an ARexx interface
with ~40 documented commands for door and session management. See
`docs/reference/arexx.md`.

### ARexx door (verified)

An ABBS door type (type `A`) that launches as an ARexx script. The
script is invoked via the ABBS ARexx interpreter and communicates
using ARexx commands. See `docs/reference/doors.md`.

### ABBS Script (verified)

A file with the `.ABBS` extension. These are ARexx scripts (text files
using ARexx syntax). They are invoked via ABBS's ARexx interpreter,
not as standalone executables. See `docs/reference/scripts.md`.

### BBS

Bulletin Board System. The host software that users dial into and that
doors run under.

### Carrier (verified)

The communications carrier signal between the user's modem and the BBS.
Carrier loss (RC=20 in ARexx) means the user has disconnected. ARexx
programs must exit immediately on RC=20. See `docs/reference/arexx.md`.

### Door

A program that a BBS user can run from the BBS's menu system. Doors
typically provide games, utilities, or external services. ABBS supports
three door types: ARexx (A), Paragon (P), and Shell (S).

### Exit Reason

A value that a door returns to the BBS to indicate why it terminated.
The ARexx interface uses RC codes (0=OK, 20=carrier loss/timeout).
Native doors may use exit codes. See `docs/reference/arexx.md`.

### Host

The development machine (typically a modern PC) used to develop and test
doors before deploying them to the target Amiga system. The host adapter
simulates a BBS environment without requiring an actual BBS.

### Local variable (verified)

An AmigaDOS process-scoped variable set by ABBS for Shell doors.
Two documented local variables: `FullName` (user's logon name) and
`NodeNr` (node number). Retrieved with `C:get`. See
`docs/reference/doors.md`.

### Node (verified)

A single user connection slot on a BBS. Each node has its own
configuration files (`Node<N>Config`, `Node<N>Menu`), its own ARexx port
(`"ABBS node #<N> port"`), its own hold directory, and isolated process
state. ABBS supports multiple simultaneous nodes.

### Paragon door (verified)

An ABBS door type (type `P`) that launches as a "Paragon door". The
Paragon protocol is a different integration surface from ARexx and
Shell. Not yet documented. See `docs/reference/doors.md`.

### Security Level

A representation of the user's access level on the BBS. In ABBS, this
is exposed as boolean sysop/sigop checks via ARexx (SYSOP, SIGOP
commands). No numeric level is documented. See
`docs/reference/arexx.md`.

### Session

The period during which a user is connected to a BBS node and is running
a door. The Session dataclass captures the BBS context (node number,
user identity, remaining time, etc.).

### Shell door (verified)

An ABBS door type (type `S`) that launches via an AmigaDOS shell script.
The shell script sets up the environment and runs a native Amiga
executable. If the script fails, the user may be dropped into an
AmigaDOS shell (security risk). See `docs/reference/doors.md`.

### Timeout (verified)

An ABBS event (RC=20) that terminates a door when the user has been
idle or out of time. Handled identically to carrier loss in the ARexx
interface. The exact timeout duration is configured in ABBS. See
`docs/reference/runtime.md`.

### User Record

The BBS's internal data structure for a user account. In ABBS, some
user data is accessible through ARexx commands (USERNAME, USERINFO,
FILEINFO, READBITS, READUSERSETUP). The internal record layout is not
documented in the extracted sources.
