# ARexx — ABBS ARexx interface reference

## Purpose

Document the ABBS ARexx interface: available commands, message-port naming
conventions, argument formats, and return conventions. This is the primary
source for future ARexx bridge adapter design.

## Source

Primary: `Docs/abbsrexx.doc`, `Docs/abbsrexx.guide`

## Evidence status

[Verified] — Both documents analysed.

## Scope

- ARexx command names and arguments
- Message-port naming pattern
- Return value conventions
- Security or access controls on commands
- Error handling and error codes
- Relationship to door lifecycle and session management

## Verified findings

### Port naming (DF-EVID-011)

- Node port format: `"ABBS node #<N> port"` where `<N>` is the node number
- Node 1 example: `"ABBS node #1 port"`
- Main program port: `"ABBS mainport"`

### Error handling conventions (DF-EVID-012)

- `RC = 0` means OK
- `RC != 0` means error; higher values mean more severe errors
- `RC = 20` means carrier lost, out of time, or user thrown out
- When RC != 0, the `RESULT` variable is NOT filled in
- Scripts must set `options results` at the top to get return values
- `options results` is only needed once per script

### Carrier loss handling (DF-EVID-013)

*ALL* ARexx commands may return RC = 20 if carrier is lost. The ARexx
program must exit immediately and return control to ABBS. This applies
to all input functions as well — if carrier loss is detected, the program
has no choice but to exit.

### Commands available in ALL ABBS versions (DF-EVID-014)

| Command | Synopsis | Returns |
|---|---|---|
| BBSNAME | Returns the BBS GRAB name (not the BBS name) | grabname string |
| BREAKOUTIMAGE | Outputs write buffer without newline | RC |
| EJECT | Ejects user on node | RC |
| FILEINFO | Returns file transfer statistics string | "downloads uploads kb_dl kb_ul" |
| GETCONSTAT | Returns baud rate and error correction | "<baud> <protocol>" |
| GETLINE | Input a line of up to <maxlength> characters | line string |
| GETNEXTPARAM | Reads next parameter from command line | param string |
| LISTEN | Makes node listen to serial port again | RC |
| MAYGETCHAR | Input a character if available | char string |
| MORE | Turns more-prompts back on | RC |
| NODENUMBER | Gets current node number | node number string |
| NOMORE | Turns off more-prompts | RC |
| OUTIMAGE | Outputs write buffer with newline | RC |
| QUICK | Returns quick-mode status | RC = 1 if quick on |
| RAW [OFF] | Disables ABBS parsing of incoming characters | RC |
| READBITS | Reads user access bits in News conference | bits string (e.g. "RUDF") |
| READCHAR | Input a single character | char string |
| READUSERSETUP | Reads user setup magic number | magic number string |
| RESUME | Resume from suspend | RC |
| SETBITS | Sets user access bits | RC |
| SETLOGINSCRIPT | Changes personal login script | RC |
| SETSTATUSTEXT | Changes node status text (max 23 chars) | RC |
| SHUTDOWN [NOBUSY] | Quit node | RC |
| SIGOP | Check if user has sigop access | RC = 1 if yes |
| SUSPEND [NOBUSY] | Releases serial port | RC |
| SYSOP | Check if user has sysop access | RC = 1 if yes |
| SYSOPNAME | Returns sysop name | name string |
| TIMELEFT | Returns time left for user | time string |
| TYPEFILE | Types a file to the user | RC |
| UNLISTEN | Stops monitoring serial port | RC |
| UNREAD | Returns number of unread News messages | count |
| USERINFO | Returns user statistics string | "timeson msgs_in msgs_read msgs_dumped msgnr" |
| USERNAME | Returns name of current user | name string |
| USERSETUP | Gets user setup (newuser script only) | RC |
| WRITECHAR | Writes character to output buffer | RC |
| WRITETEXT | Writes text to output buffer | RC |

### Commands available in ABBS v2.x/3.x (DF-EVID-015)

| Command | Synopsis |
|---|---|
| CLEARCALLERINFO | Clears boardstats file |
| REALBBSNAME | Returns the actual BBS name |

### Commands available in ABBS v3.0+ (DF-EVID-016)

| Command | Synopsis | Input |
|---|---|---|
| SETNODEINFO | Sets speed and caller in WHO | `<speed> <user>` |
| GETNODEINFO | Gets node info from current node | None; returns "nodenumber speed citystate" |

### Commands available in ABBS v3.1+ (DF-EVID-017)

| Command | Synopsis |
|---|---|
| SETNODECITY | Sets CityState in WHO |
| SETNODEUSER | Sets User in WHO |
| SETNODESPEED | Sets speed in WHO |
| GETNODECITY | Gets CityState from WHO |
| GETNODEUSER | Gets username from WHO |
| GETNODESPEED | Gets speed from WHO |

### Commands available in ABBS v3.2+ (DF-EVID-018)

| Command | Synopsis |
|---|---|
| CLEARCALLERINFOENTRIES | Clears specific caller info entries (1-14) |

### Session-related ARexx commands (DF-EVID-019)

The following commands are directly relevant to populating a `Session`:

| Session field | ARexx command | Notes |
|---|---|---|
| node_number | NODENUMBER | Returns node number as string |
| display_name | USERNAME | Returns current user's name |
| minutes_remaining | TIMELEFT | Returns time left (format unknown) |
| is_local | GETCONSTAT | Baud 0 = local; also returns protocol |
| user_id | (not available) | No numeric user ID command found |
| security_level | SYSOP / SIGOP | Boolean: sysop access or not; no numeric level |
| terminal capabilities | READUSERSETUP | Magic number encodes charset, pagelength, protocol, ANSI, colour, etc. |
| connected state | (GETCONSTAT) | Implied by baud rate presence |

### USERSETUP magic number format (DF-EVID-020)

The `READUSERSETUP` command returns a 32-bit magic number encoding user
terminal preferences. Format (bit fields):

| Bits | Field | Values |
|---|---|---|
| 29-32 | Unused | Must be 0 |
| 24-28 | Charset | 0=ISO, 1=IBM, 2=IBN, 3=US7, 4=UK7, 5=GE7, 6=FR7, 7=SF7, 8=NO7, 9=DE7, 10=SP7, 11=IT7, 12=MAC |
| 16-23 | Page length | 0 = unlimited |
| 12-15 | Scratchpad format | 0=text, 1=arc, 2=lzh, 3=zip, 4=lha, 5=arj, 6=Zoo, 7=Lzx |
| 8-11 | Transfer protocol | 0=none, 1=zmodem, 2=xmodem, 3=xmodem-CRC, 4=ymodem, 5=ymodembatch, 6=ymodemG |
| 7 | ReadRef/Read | Bit flag |
| 6 | Raw files | Bit flag |
| 5 | Clear screen | Bit flag |
| 4 | ANSI terminal | Bit flag |
| 3 | G&R protocol | Bit flag |
| 2 | Colour in messages | Bit flag |
| 1 | ANSI menus | Bit flag |
| 0 | FSE | Bit flag |

This is the primary source for terminal capability detection.

### GETCONSTAT return format (DF-EVID-021)

Returns `<baud> <error_correction>` where:
- Baud 0 = local connection
- Error correction: `None`, `MNP`, `42BIS`, `NULL` (Nullmodem)

### FILEINFO return format (DF-EVID-022)

Returns `<downloads> <uploads> <kb_dled> <kb_uled>` (space-separated).

### USERINFO return format (DF-EVID-023)

Returns `<timeson> <msgs_entered> <msgs_read> <msgs_dumped> <userinfomsgnr>`.

### Main port commands (DF-EVID-024)

Main port (`"ABBS mainport"`) supports:

| Command | Synopsis |
|---|---|
| SHOWGUI [OFF] | Opens/closes the BBS GUI |
| SHUTDOWN | Quit the BBS (RC=5 if nodes not down) |
| STARTNODE | Starts a new node with a given config file |

## Partial findings

### TIMELEFT return format

The documentation does not specify whether TIMELEFT returns seconds, minutes,
or a formatted string. The typical ABBS value is likely minutes or seconds
but this needs verification. [Partial]

### GETLINE RC values

RC = 10 documented for "Missing Parameters" but the command takes `<max length>`
as a required parameter. The RC = 10 case presumably means no parameter was
provided. [Partial]

## Unknowns

- Is there a command to read the user record (beyond USERNAME)?
- Is there a command to read numeric user ID?
- Are there undocumented commands in later ABBS versions?
- What is the exact TIMELEFT return format?
- What is the baud-rate mapping for GETCONSTAT?

## Runtime verification required

- Confirm the actual TIMELEFT format
- Confirm that all 40 documented commands work as documented
- Check for undocumented commands in the actual running system
- Verify RC = 20 behaviour on actual carrier loss

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-011 | abbsrexx.doc | Verified | Port naming convention | ARexx adapter |
| DF-EVID-012 | abbsrexx.doc | Verified | RC convention (0=OK, !=0=error, 20=carrier) | ExitReason |
| DF-EVID-013 | abbsrexx.doc | Verified | Carrier loss forces immediate exit | ExitReason, timeout |
| DF-EVID-014 | abbsrexx.doc | Verified | All-version command list (33 commands) | ARexx adapter |
| DF-EVID-015 | abbsrexx.doc | Verified | v2.x/3.x commands (2 commands) | ARexx adapter |
| DF-EVID-016 | abbsrexx.guide | Verified | v3.0+ commands (2 commands) | ARexx adapter |
| DF-EVID-017 | abbsrexx.doc | Verified | v3.1+ commands (6 commands) | ARexx adapter |
| DF-EVID-018 | abbsrexx.doc | Verified | v3.2+ commands (1 command) | ARexx adapter |
| DF-EVID-019 | abbsrexx.doc | Verified | Session-relevant ARexx commands | Session fields |
| DF-EVID-020 | abbsrexx.doc | Verified | USERSETUP magic number format | Terminal capabilities |
| DF-EVID-021 | abbsrexx.doc | Verified | GETCONSTAT return format | Connection, local/remote |
| DF-EVID-022 | abbsrexx.doc | Verified | FILEINFO return format | File transfer stats |
| DF-EVID-023 | abbsrexx.doc | Verified | USERINFO return format | User statistics |
| DF-EVID-024 | abbsrexx.doc | Verified | Main port commands | BBS management |

## Cross-references

- `docs/reference/doors.md` — ARexx door type (type A)
- `docs/reference/scripts.md` — ARexx script syntax in DAYS.ABBS
- `docs/reference/environment.md` — Environment vs ARexx context
- `docs/reference/runtime.md` — RC=20 carrier loss behaviour
- `docs/spec/session-model.md` — Session field validation
