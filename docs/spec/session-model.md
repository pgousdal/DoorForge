# Provisional session model

This model is intentionally BBS-neutral and is not yet a frozen public ABI.

A DoorForge session needs, at minimum:

- adapter kind;
- node number;
- user identifier;
- display name;
- security level;
- remaining time;
- local/remote flag;
- terminal capabilities;
- connected/disconnected state;
- explicit exit reason.

## Proposed exit reasons

- normal return;
- user quit;
- timeout;
- carrier loss;
- BBS shutdown;
- adapter error;
- door failure.

No ABBS-specific field mapping is considered verified in M0.
