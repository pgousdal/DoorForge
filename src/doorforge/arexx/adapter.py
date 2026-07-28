from __future__ import annotations

import time
from typing import Callable, TextIO

from ..session import ExecuteResult, ExitReason, Session

from .client import (
    ArexxClient,
    ArexxConnectionError,
    ArexxProtocolError,
    ArexxResult,
)


def _int_or_zero(raw: str) -> int:
    try:
        return int(raw.strip())
    except (ValueError, AttributeError):
        return 0


def _parse_timeleft(raw: str) -> int:
    """Parse TIMELEFT and return minutes remaining.

    Verified evidence (DF-EVID-034): TIMELEFT is available in all ABBS
    versions.  The return format is not documented.

    **Adapter assumption**: the value is in **seconds**; the adapter
    converts to minutes via ``max(0, seconds // 60)``.  If ABBS returns
    a different unit (e.g. minutes, or a formatted string) this
    conversion will be incorrect.

    The raw value is **not** discarded — it can be inspected via the
    mock client's ``call_log`` in tests, or via a real client's logging
    on the target system.
    """
    seconds = _int_or_zero(raw)
    return max(0, seconds // 60)


def _parse_constat(raw: str) -> bool:
    """Return True if GETCONSTAT indicates a local connection.

    DF-EVID-021: GETCONSTAT returns '<baud> <protocol>'.  Baud 0 = local.
    """
    parts = raw.strip().split(None, 1)
    if not parts:
        return False
    try:
        return int(parts[0]) == 0
    except ValueError:
        return False


class ArexxAdapter:
    """Host-testable ARexx door adapter.

    Uses an ``ArexxClient`` to communicate with an ABBS node ARexx port.
    All behaviour is driven by verified DF-EVID evidence.  Undocumented
    behaviour produces explicit errors or documented limitations.
    """

    def __init__(self, client: ArexxClient) -> None:
        self._client = client
        self._adapter_kind = "arexx"

    @property
    def adapter_kind(self) -> str:
        return self._adapter_kind

    def build_session(self) -> Session:
        """Populate a Session using verified ARexx commands.

        Verified commands used (DF-EVID-019):
            NODENUMBER    -> Session.node_number
            USERNAME      -> Session.display_name
            TIMELEFT      -> Session.minutes_remaining (see _parse_timeleft)
            GETCONSTAT    -> Session.is_local (baud 0 = local)
            SYSOP         -> Session.is_sysop (RC 1 = sysop)

        Unsupported fields (set to ``None`` — no ABBS evidence):
            user_id         (DF-EVID-035: no numeric user ID surface)
            security_level  (ABBS exposes boolean sysop only; not numeric)

        Raises:
            ArexxConnectionError: If the ARexx port is unreachable.
            ArexxProtocolError: If a response cannot be parsed.
        """
        node = self._client.call("NODENUMBER")
        name = self._client.call("USERNAME")
        timeleft = self._client.call("TIMELEFT")
        constat = self._client.call("GETCONSTAT")
        sysop = self._client.call("SYSOP")

        return Session(
            node_number=_int_or_zero(node.result),
            display_name=name.result or "?",
            is_local=_parse_constat(constat.result),
            minutes_remaining=_parse_timeleft(timeleft.result),
            is_sysop=(sysop.rc == 1),
            user_id=None,
            security_level=None,
        )

    def execute(
        self,
        script_path: str,
        *,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
        on_input: Callable[[str], str] | None = None,
        on_output: Callable[[str], None] | None = None,
    ) -> ExecuteResult:
        """Execute a door script and return the result.

        In a real ABBS deployment this sends the script to the node's
        ARexx port.  In host testing mode the script is run through the
        mock client, which returns canned ARexx responses.

        The caller must provide either stdin/stdout file objects or
        on_input/on_output callbacks for user I/O proxying.

        Args:
            script_path: Path to the .ABBS door script.
            stdin: Input stream (used if on_input is None).
            stdout: Output stream (used if on_output is None).
            on_input: Called when the door requests user input.
            on_output: Called when the door sends output text.

        Returns:
            An ExecuteResult with the semantic exit reason and the raw
            RC from the underlying command.

        Raises:
            ArexxConnectionError: If the ARexx port is unreachable.
            RuntimeError: If no I/O callbacks are provided.
        """
        _input = on_input if on_input else _stdin_reader(stdin)
        _output = on_output if on_output else _stdout_writer(stdout)

        _output(f"Executing: {script_path}")

        result = self._client.call("EXECUTE", script_path)

        if result.rc == 0:
            _output("Completed successfully")
            return ExecuteResult(reason=ExitReason.NORMAL, raw_rc=0)
        if result.rc == 20:
            _output("Carrier lost or timeout (RC=20 — cannot distinguish)")
            return ExecuteResult(
                reason=ExitReason.CARRIER_LOSS_OR_TIMEOUT, raw_rc=20
            )
        if result.rc == 5:
            _output("No active user on node")
            return ExecuteResult(reason=ExitReason.ADAPTER_ERROR, raw_rc=5)

        _output(f"Script failed with RC={result.rc}")
        return ExecuteResult(reason=ExitReason.DOOR_FAILURE, raw_rc=result.rc)

    def close(self) -> None:
        """Close the ARexx client connection."""
        self._client.close()


def _stdin_reader(stream: TextIO | None) -> Callable[[str], str]:
    def reader(prompt: str) -> str:
        if stream is None:
            return ""
        return stream.readline().rstrip("\n")

    return reader


def _stdout_writer(stream: TextIO | None) -> Callable[[str], None]:
    def writer(text: str) -> None:
        if stream is not None:
            stream.write(text + "\n")

    return writer
