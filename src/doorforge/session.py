from dataclasses import dataclass
from enum import Enum


class ExitReason(str, Enum):
    NORMAL = "normal"
    USER_QUIT = "user_quit"
    TIMEOUT = "timeout"
    CARRIER_LOSS = "carrier_loss"
    BBS_SHUTDOWN = "bbs_shutdown"
    ADAPTER_ERROR = "adapter_error"
    DOOR_FAILURE = "door_failure"


@dataclass(frozen=True)
class Session:
    user_id: int
    node_number: int
    security_level: int
    minutes_remaining: int
    is_local: bool
    display_name: str

    def validate(self) -> None:
        if self.user_id < 0:
            raise ValueError("user_id must be non-negative")
        if self.node_number < 0:
            raise ValueError("node_number must be non-negative")
        if self.security_level < 0:
            raise ValueError("security_level must be non-negative")
        if self.minutes_remaining < 0:
            raise ValueError("minutes_remaining must be non-negative")
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")
