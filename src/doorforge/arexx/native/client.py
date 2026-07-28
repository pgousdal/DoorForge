from __future__ import annotations

import subprocess
import sys

from ..client import (
    ArexxClient,
    ArexxConnectionError,
    ArexxProtocolError,
    ArexxResult,
    abbs_port_name,
)


class AmigaArexxClient(ArexxClient):
    """Native Amiga ARexx client that communicates via the ``arexx-cli`` helper.

    This client invokes the compiled ``arexx-cli`` executable (an ANSI C
    program) to send commands to an ABBS node's ARexx port.  The helper
    handles all AmigaOS-specific ARexx messaging.

    On non-Amiga hosts the constructor will succeed but every ``call()``
    will raise :exc:`ArexxConnectionError` because the ``arexx-cli``
    executable is not available.

    Args:
        node: The ABBS node number to connect to.
        helper: Path to the ``arexx-cli`` executable.  Defaults to
            ``"arexx-cli"`` (found via ``$PATH``).
        timeout: Timeout in seconds for each command invocation.
    """

    def __init__(
        self, node: int, helper: str = "arexx-cli", timeout: float = 30.0
    ) -> None:
        self._node = node
        self._helper = helper
        self._timeout = timeout
        self._closed = False

        # Validate node immediately so errors surface at construction time.
        abbs_port_name(node)

    def call(self, command: str, *args: str) -> ArexxResult:
        if self._closed:
            raise ArexxConnectionError("client is closed")

        try:
            completed = subprocess.run(
                [self._helper, str(self._node), command.upper(), *args],
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
        except FileNotFoundError:
            raise ArexxConnectionError(
                f"native ARexx helper not found: {self._helper}; "
                f"arexx-cli must be compiled and installed on AmigaOS"
            )
        except subprocess.TimeoutExpired:
            raise ArexxConnectionError(
                f"native ARexx helper timed out after {self._timeout}s"
            )
        # OSError for permission-denied, etc.
        except OSError as exc:
            raise ArexxConnectionError(
                f"failed to launch native helper: {exc}"
            )

        if completed.returncode != 0:
            err = completed.stdout.strip() or completed.stderr.strip()
            raise ArexxConnectionError(
                f"native helper failed (rc={completed.returncode}): {err}"
            )

        return _parse_helper_output(completed.stdout)

    def close(self) -> None:
        self._closed = True


def _unescape(text: str) -> str:
    """Unescape C-style sequences emitted by ``arexx-cli``.

    The helper escapes ``\\``, ``\\n``, and ``\\r`` to preserve
    protocol line integrity.  Unescape order: ``\\\\`` -> ``\\``
    first to avoid misinterpreting ``\\n`` in a backslash-escaped ``n``.
    """
    return (
        text.replace("\\\\", "\x00")
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\x00", "\\")
    )


def _parse_helper_output(text: str) -> ArexxResult:
    """Parse ``arexx-cli`` stdout into an :class:`ArexxResult`.

    Expected output format::

        RC:<number>
        RESULT:<optional C-escaped text>

    Or on transport error::

        ERROR:<description>

    RESULT and ERROR values are C-escaped by the helper (``\\n``, ``\\r``,
    ``\\\\``).  The parser unescapes them.
    """
    rc: int | None = None
    result: str = ""
    error: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("RC:"):
            if rc is None:  # first RC line wins
                try:
                    rc = int(stripped[3:].strip())
                except (ValueError, IndexError):
                    raise ArexxProtocolError(
                        f"cannot parse RC from helper output: {line!r}"
                    )
        elif stripped.startswith("RESULT:"):
            if not result:  # first RESULT line wins
                idx = line.index("RESULT:")
                result = _unescape(line[idx + 7 :])
        elif stripped.startswith("ERROR:"):
            idx = line.index("ERROR:")
            error = _unescape(line[idx + 6 :])
        # else ignore unrecognised lines (forward-compat)

    if error is not None:
        raise ArexxConnectionError(f"native helper: {error}")

    if rc is None:
        raise ArexxProtocolError(
            "native helper output missing RC line: "
            + repr(text.strip()[:200])
        )

    return ArexxResult(rc=rc, result=result)
