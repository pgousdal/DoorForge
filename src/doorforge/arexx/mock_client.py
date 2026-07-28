from __future__ import annotations

from .client import ArexxClient, ArexxConnectionError, ArexxResult


class MockArexxClient(ArexxClient):
    """Deterministic ARexx client for host-side testing.

    Responses are pre-loaded per command name. Each command can be
    called multiple times and returns the same canned response.
    """

    def __init__(self) -> None:
        self._responses: dict[str, ArexxResult] = {}
        self._call_log: list[tuple[str, tuple[str, ...]]] = []
        self._closed = False

    def expect(self, command: str, rc: int, result: str = "") -> None:
        """Register a canned response for *command*."""
        self._responses[command.upper()] = ArexxResult(rc=rc, result=result)

    def expect_carrier_loss(self, command: str) -> None:
        """Convenience: register RC=20 for *command*."""
        self.expect(command, rc=20)

    def expect_error(self, command: str, rc: int = 1, result: str = "") -> None:
        """Convenience: register a non-zero, non-20 RC for *command*."""
        self.expect(command, rc=rc, result=result)

    @property
    def call_log(self) -> list[tuple[str, tuple[str, ...]]]:
        """Return the list of (command, args) calls made."""
        return list(self._call_log)

    def reset(self) -> None:
        """Clear all expectations and the call log."""
        self._responses.clear()
        self._call_log.clear()
        self._closed = False

    # --- ArexxClient interface ---

    def call(self, command: str, *args: str) -> ArexxResult:
        if self._closed:
            raise ArexxConnectionError("client is closed")
        key = command.upper()
        self._call_log.append((key, args))
        if key not in self._responses:
            raise ArexxConnectionError(
                f"no expectation registered for {key}"
            )
        return self._responses[key]

    def close(self) -> None:
        self._closed = True
