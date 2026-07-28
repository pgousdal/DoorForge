from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ArexxResult:
    """Result of an ARexx command call.

    Attributes:
        rc: Return code. 0 = OK, 20 = carrier loss or timeout, other = error.
        result: The RESULT string from the command. Only valid when rc == 0.
    """

    rc: int
    result: str


class ArexxClient(ABC):
    """Abstract interface for communicating with an ABBS node ARexx port."""

    @abstractmethod
    def call(self, command: str, *args: str) -> ArexxResult:
        """Send an ARexx command and return its result.

        Args:
            command: The ARexx command name (e.g. NODENUMBER, USERNAME).
            *args: Optional command arguments.

        Returns:
            An ArexxResult with rc and result string.

        Raises:
            ArexxConnectionError: If the ARexx port is unreachable.
            ArexxProtocolError: If the response cannot be parsed.
        """

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the ARexx port."""


class ArexxConnectionError(RuntimeError):
    """Raised when the ARexx port is unreachable."""


class ArexxProtocolError(RuntimeError):
    """Raised when an ARexx response cannot be parsed."""


def abbs_port_name(node: int) -> str:
    """Return the verified ABBS ARexx port name for *node*.

    Format: ``"ABBS node #<N> port"`` (DF-EVID-011).

    Raises:
        ValueError: If *node* is negative.
    """
    if node < 0:
        raise ValueError(f"node must be non-negative, got {node}")
    return f"ABBS node #{node} port"
