from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExitReason(str, Enum):
    NORMAL = "normal"
    USER_QUIT = "user_quit"
    TIMEOUT = "timeout"
    CARRIER_LOSS = "carrier_loss"
    CARRIER_LOSS_OR_TIMEOUT = "carrier_loss_or_timeout"
    BBS_SHUTDOWN = "bbs_shutdown"
    ADAPTER_ERROR = "adapter_error"
    DOOR_FAILURE = "door_failure"


@dataclass(frozen=True)
class ExecuteResult:
    """Result of an adapter execute() call.

    Attributes:
        reason: The semantic exit reason determined by the adapter.
        raw_rc: The raw return code from the BBS or subprocess, if
            available.  This preserves information the adapter's
            reason mapping may have condensed (e.g. RC=20 maps to
            ``CARRIER_LOSS_OR_TIMEOUT`` but the caller can still
            inspect *raw_rc* to see that it was 20).
    """

    reason: ExitReason
    raw_rc: int | None = None


@dataclass(frozen=True)
class Session:
    """BBS-neutral representation of a connected user.

    Verified fields (supported by DF-EVID evidence for ABBS):
        node_number, display_name, is_local, minutes_remaining, is_sysop.

    Provisional fields (no ABBS evidence, kept for other BBS platforms):
        user_id, security_level.  Set to ``None`` when unavailable.
    """

    node_number: int
    display_name: str
    is_local: bool
    minutes_remaining: int
    is_sysop: bool
    user_id: int | None = None
    security_level: int | None = None

    def validate(self) -> None:
        if self.user_id is not None and self.user_id < 0:
            raise ValueError("user_id must be non-negative")
        if self.node_number < 0:
            raise ValueError("node_number must be non-negative")
        if self.security_level is not None and self.security_level < 0:
            raise ValueError("security_level must be non-negative")
        if self.minutes_remaining < 0:
            raise ValueError("minutes_remaining must be non-negative")
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")
