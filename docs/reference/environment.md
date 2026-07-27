# Environment — ABBS environment and local variables reference

## Purpose

Document all variables that ABBS makes available to doors and scripts.
This is the primary source for the `Session` construction logic in
every adapter.

## Source

Primary: `Docs/Doors.doc`, `Docs/abbsrexx.doc`
Supporting: `Doors/DAYS/DAYS.ABBS`

## Evidence status

[Partial] — Local variables documented in Doors.doc. ARexx commands
provide additional session data. Environment variables for Shell doors
are not documented.

## Scope

- Local variables set before door invocation
- ARexx commands that return session data
- Environment variables for Shell doors
- How node identity, user identity, security level, and remaining time
  are conveyed

## Verified findings

### Local variables for Shell doors (DF-EVID-008)

From Doors.doc, Shell doors receive two local (process-scoped) variables:

| Variable | Content | Retrieval |
|---|---|---|
| `FullName` | User's logon name | `C:get fullname` |
| `NodeNr` | Node number | `C:get Nodenr` |

These are AmigaDOS local variables, not environment variables. They are
set by ABBS in the Shell door's process context. The `C:get` AmigaDOS
command reads them.

### ARexx commands that provide session data (DF-EVID-019)

ARexx doors use the following commands to get session context:

| Command | Returns | Session equivalent |
|---|---|---|
| NODENUMBER | Node number (string) | node_number |
| USERNAME | User's display name (string) | display_name |
| TIMELEFT | Time remaining (format unclear) | minutes_remaining |
| GETCONSTAT | Baud rate and protocol; baud=0 means local | is_local |
| SYSOP | RC=1 if user has sysop access | security_level (boolean) |
| SIGOP | RC=1 if user has sigop access | security_level (boolean) |
| READUSERSETUP | Magic number encoding terminal capabilities | Terminal capabilities |
| USERINFO | Statistics string | (session metadata) |

### TIMELEFT availability (DF-EVID-034)

The `TIMELEFT` ARexx command is available in ALL ABBS versions. It
returns the remaining time for the current user. The exact format
(seconds, minutes, formatted string) is not specified in the
documentation.

### Direct session field mapping (DF-EVID-035)

Based on combined evidence from Doors.doc and abbsrexx.doc:

| Session field | Source | How obtained |
|---|---|---|
| node_number | Doors.doc (NodeNr) / abbsrexx (NODENUMBER) | Local variable or ARexx command |
| display_name | Doors.doc (FullName) / abbsrexx (USERNAME) | Local variable or ARexx command |
| minutes_remaining | abbsrexx (TIMELEFT) | ARexx command |
| is_local | abbsrexx (GETCONSTAT, baud=0) | ARexx command |
| user_id | No evidence | Cannot populate from current evidence |
| security_level | abbsrexx (SYSOP/SIGOP — boolean only) | ARexx command, but no numeric level |

## Partial findings

### No documented environment variables

The Doors.doc and abbsrexx.doc documents do not describe POSIX-style
environment variables. Shell doors use AmigaDOS local variables set in
the process scope. ARexx doors use ARexx commands. It is possible that
ABBS also sets environment variables for native executables, but this
is not documented in the sources examined. [Partial]

### TIMELEFT format

The TIMELEFT command is documented but its return format is unspecified.
It may return seconds (e.g., "1200") or a formatted string (e.g., "20m").
This must be confirmed. [Partial]

### Security level is boolean only

SYSOP and SIGOP return boolean values (RC=1 for yes, RC=0 for no). There
is no evidence of a numeric security or access level similar to the
provisional `security_level` field. ABBS may use a numeric level
internally but does not expose it through the documented ARexx commands
or local variables. [Partial]

## Unknowns

- Are any environment variables set for Shell doors beyond local variables?
- Are environment variables set for native (Paragon) doors?
- What is the exact TIMELEFT return format?
- Is there a numeric user ID anywhere in the ABBS data model?
- How is the user's home directory or file area conveyed?
- What is the baud-rate mapping for GETCONSTAT?
- Are there conditional variables based on user flags?

## Runtime verification required

- Print all ARexx variables and local vars from a Shell door to capture
  everything ABBS sets
- Examine TIMELEFT return format at runtime
- Confirm GETCONSTAT baud values on actual modem connections
- Check for environment variables using `C:list env:` from a Shell door

## Evidence registry

| ID | Source | Class | Description | Relates to |
|---|---|---|---|---|
| DF-EVID-008 | Doors.doc | Verified | Local variables FullName and NodeNr | Shell door adapter |
| DF-EVID-019 | abbsrexx.doc | Verified | Session-relevant ARexx commands | Session fields |
| DF-EVID-034 | abbsrexx.doc | Verified | TIMELEFT available in all ABBS versions | Session.minutes_remaining |
| DF-EVID-035 | both | Verified | Combined session field mapping | Adapter interface |

## Cross-references

- `docs/reference/doors.md` — Local variable mechanism
- `docs/reference/arexx.md` — ARexx commands for session data
- `docs/reference/scripts.md` — Script variable context
- `docs/reference/runtime.md` — Runtime variable verification
- `docs/spec/session-model.md` — Session fields to validate
