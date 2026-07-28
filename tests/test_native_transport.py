"""Host-side tests for the native Amiga ARexx transport.

These tests mock the ``arexx-cli`` subprocess so they run on any host
without requiring AmigaOS or the compiled helper executable.
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from doorforge import abbs_port_name
from doorforge.arexx.client import (
    ArexxConnectionError,
    ArexxProtocolError,
    ArexxResult,
)
from doorforge.arexx.native.client import (
    AmigaArexxClient,
    _parse_helper_output,
    _unescape,
)


# ---------------------------------------------------------------------------
# abbs_port_name tests  (Task 4)
# ---------------------------------------------------------------------------


class TestAbbsPortName(unittest.TestCase):
    """Verify the ABBS port naming convention (DF-EVID-011)."""

    def test_node_0(self):
        self.assertEqual(abbs_port_name(0), "ABBS node #0 port")

    def test_node_1(self):
        self.assertEqual(abbs_port_name(1), "ABBS node #1 port")

    def test_node_42(self):
        self.assertEqual(abbs_port_name(42), "ABBS node #42 port")

    def test_multi_digit(self):
        self.assertEqual(abbs_port_name(999), "ABBS node #999 port")

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            abbs_port_name(-1)

    def test_exact_case_and_spacing(self):
        """Verify the exact string matches abbsrexx.doc documentation."""
        name = abbs_port_name(1)
        self.assertEqual(name, "ABBS node #1 port")
        # Verify no unexpected whitespace
        self.assertNotIn("  ", name)
        self.assertFalse(name.startswith(" "))
        self.assertFalse(name.endswith(" "))


# ---------------------------------------------------------------------------
# _unescape tests
# ---------------------------------------------------------------------------


class TestUnescape(unittest.TestCase):
    """C-escape unescaping used by the native helper parser."""

    def test_plain_text_passthrough(self):
        self.assertEqual(_unescape("Hello"), "Hello")

    def test_newline_unescaped(self):
        self.assertEqual(_unescape("line1\\nline2"), "line1\nline2")

    def test_carriage_return_unescaped(self):
        self.assertEqual(_unescape("line1\\rline2"), "line1\rline2")

    def test_backslash_unescaped(self):
        self.assertEqual(_unescape("a\\\\b"), "a\\b")

    def test_all_three_sequences(self):
        self.assertEqual(
            _unescape("a\\\\b\\nc\\rd"),
            "a\\b\nc\rd",
        )

    def test_no_escape_sequences(self):
        self.assertEqual(_unescape(""), "")

    def test_consecutive_escapes(self):
        self.assertEqual(
            _unescape("\\\\\\n\\\\\\r"),
            "\\\n\\\r",
        )


# ---------------------------------------------------------------------------
# _parse_helper_output tests
# ---------------------------------------------------------------------------


class TestParseHelperOutput(unittest.TestCase):
    """Parse the arexx-cli stdout protocol."""

    def test_rc_zero_with_result(self):
        r = _parse_helper_output("RC:0\nRESULT:Hello\n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "Hello")

    def test_rc_zero_with_empty_result(self):
        r = _parse_helper_output("RC:0\nRESULT:\n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "")

    def test_rc_twenty_with_no_result(self):
        r = _parse_helper_output("RC:20\nRESULT:\n")
        self.assertEqual(r.rc, 20)
        self.assertEqual(r.result, "")

    def test_rc_arbitrary(self):
        r = _parse_helper_output("RC:42\nRESULT:some error\n")
        self.assertEqual(r.rc, 42)

    def test_extra_whitespace(self):
        r = _parse_helper_output("  RC:  0  \n  RESULT:  hello  \n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "  hello  ")  # preserves after RESULT:

    def test_error_line_raises(self):
        with self.assertRaises(ArexxConnectionError):
            _parse_helper_output("ERROR:Port not found: ABBS node #1 port\n")

    def test_missing_rc_raises(self):
        with self.assertRaises(ArexxProtocolError):
            _parse_helper_output("RESULT:hello\n")

    def test_invalid_rc_raises(self):
        with self.assertRaises(ArexxProtocolError):
            _parse_helper_output("RC:notanumber\nRESULT:\n")

    def test_multiline_result(self):
        r = _parse_helper_output("RC:0\nRESULT:line1\n")
        self.assertEqual(r.result, "line1")

    def test_escaped_backslash_in_result(self):
        r = _parse_helper_output("RC:0\nRESULT:a\\\\b\n")
        self.assertEqual(r.result, "a\\b")

    def test_escaped_newline_in_result(self):
        r = _parse_helper_output("RC:0\nRESULT:line1\\nline2\n")
        self.assertEqual(r.result, "line1\nline2")

    def test_escaped_cr_in_result(self):
        r = _parse_helper_output("RC:0\nRESULT:hello\\rworld\n")
        self.assertEqual(r.result, "hello\rworld")

    def test_result_looks_like_rc(self):
        r = _parse_helper_output("RC:0\nRESULT:RC:42\n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "RC:42")

    def test_result_looks_like_error(self):
        r = _parse_helper_output("RC:0\nRESULT:ERROR:nope\n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "ERROR:nope")

    def test_error_escaped_backslash(self):
        with self.assertRaises(ArexxConnectionError) as ctx:
            _parse_helper_output("ERROR:path\\\\file\n")
        self.assertIn("path\\file", str(ctx.exception))

    def test_multiple_rc_lines_takes_first(self):
        r = _parse_helper_output("RC:0\nRESULT:a\nRC:1\n")
        self.assertEqual(r.rc, 0)

    def test_extra_lines_before_rc_ignored(self):
        r = _parse_helper_output("IGNORED\nRC:0\nRESULT:ok\n")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "ok")


# ---------------------------------------------------------------------------
# AmigaArexxClient tests (with mocked subprocess)
# ---------------------------------------------------------------------------


class TestAmigaArexxClient(unittest.TestCase):
    """AmigaArexxClient tests with mocked subprocess."""

    def _make_mock_run(self, stdout: str, rc: int = 0) -> MagicMock:
        """Return a mock ``subprocess.run`` that returns *stdout*."""
        mock = MagicMock()
        mock.returncode = rc
        mock.stdout = stdout
        mock.stderr = ""
        return mock

    # --- call() ---

    @patch("subprocess.run")
    def test_call_sends_upper_cased_command(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:0\nRESULT:1\n")
        client = AmigaArexxClient(node=1)
        client.call("NODENUMBER")

        args, _ = mock_run.call_args
        helper_args = args[0]
        self.assertIn("arexx-cli", helper_args[0])
        self.assertEqual(helper_args[1], "1")  # node
        self.assertEqual(helper_args[2], "NODENUMBER")  # uppercased

    @patch("subprocess.run")
    def test_call_with_args(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:0\nRESULT:ok\n")
        client = AmigaArexxClient(node=2)
        client.call("EXECUTE", "doors/days.abbs")

        args, _ = mock_run.call_args
        helper_args = args[0]
        self.assertEqual(helper_args[2], "EXECUTE")
        self.assertEqual(helper_args[3], "doors/days.abbs")

    @patch("subprocess.run")
    def test_call_returns_arexx_result(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:0\nRESULT:Alice\n")
        client = AmigaArexxClient(node=1)

        result = client.call("USERNAME")

        self.assertIsInstance(result, ArexxResult)
        self.assertEqual(result.rc, 0)
        self.assertEqual(result.result, "Alice")

    @patch("subprocess.run")
    def test_call_rc_20_preserved(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:20\nRESULT:\n")
        client = AmigaArexxClient(node=1)

        result = client.call("GETLINE")

        self.assertEqual(result.rc, 20)
        self.assertEqual(result.result, "")

    @patch("subprocess.run")
    def test_call_after_close_raises(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:0\nRESULT:1\n")
        client = AmigaArexxClient(node=1)
        client.close()

        with self.assertRaises(ArexxConnectionError):
            client.call("NODENUMBER")

    # --- error handling ---

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_helper_not_found_raises(self, mock_run):
        client = AmigaArexxClient(node=1)

        with self.assertRaises(ArexxConnectionError) as ctx:
            client.call("NODENUMBER")
        self.assertIn("arexx-cli", str(ctx.exception))

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(
        cmd=["arexx-cli"], timeout=5.0, output=""
    ))
    def test_timeout_raises(self, mock_run):
        client = AmigaArexxClient(node=1, timeout=5.0)

        with self.assertRaises(ArexxConnectionError) as ctx:
            client.call("NODENUMBER")
        self.assertIn("timed out", str(ctx.exception))

    @patch("subprocess.run", side_effect=PermissionError(
        "[Errno 13] Permission denied"
    ))
    def test_oserror_raises(self, mock_run):
        client = AmigaArexxClient(node=1)

        with self.assertRaises(ArexxConnectionError) as ctx:
            client.call("NODENUMBER")
        self.assertIn("Permission denied", str(ctx.exception))

    @patch("subprocess.run")
    def test_helper_nonzero_exit_raises(self, mock_run):
        mock_run.return_value = self._make_mock_run(
            stdout="ERROR:Port not found\n", rc=1
        )
        client = AmigaArexxClient(node=1)

        with self.assertRaises(ArexxConnectionError) as ctx:
            client.call("NODENUMBER")
        self.assertIn("Port not found", str(ctx.exception))

    @patch("subprocess.run")
    def test_helper_error_with_stderr(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="arexx.library not found"
        )
        client = AmigaArexxClient(node=1)

        with self.assertRaises(ArexxConnectionError) as ctx:
            client.call("NODENUMBER")
        self.assertIn("arexx.library", str(ctx.exception))

    # --- construction ---

    def test_negative_node_raises_at_construction(self):
        with self.assertRaises(ValueError):
            AmigaArexxClient(node=-1)

    def test_default_helper_path(self):
        client = AmigaArexxClient(node=1)
        self.assertEqual(client._helper, "arexx-cli")

    def test_custom_helper_path(self):
        client = AmigaArexxClient(node=1, helper="/path/to/helper")
        self.assertEqual(client._helper, "/path/to/helper")

    def test_default_timeout(self):
        client = AmigaArexxClient(node=1)
        self.assertEqual(client._timeout, 30.0)

    def test_custom_timeout(self):
        client = AmigaArexxClient(node=1, timeout=60.0)
        self.assertEqual(client._timeout, 60.0)

    # --- close() ---

    @patch("subprocess.run")
    def test_close_then_call_raises(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:0\nRESULT:1\n")
        client = AmigaArexxClient(node=1)
        client.close()

        with self.assertRaises(ArexxConnectionError):
            client.call("NODENUMBER")

    def test_close_twice_does_not_raise(self):
        client = AmigaArexxClient(node=1)
        client.close()
        client.close()  # must not raise

    # --- call_log wrapper (forward-compat) ---

    @patch("subprocess.run")
    def test_call_preserves_raw_rc_in_result(self, mock_run):
        mock_run.return_value = self._make_mock_run("RC:20\nRESULT:\n")
        client = AmigaArexxClient(node=1)
        result = client.call("GETLINE")
        self.assertEqual(result.rc, 20)


# ---------------------------------------------------------------------------
# Integration contract: AmigaArexxClient satisfies ArexxClient ABC
# ---------------------------------------------------------------------------


class TestAmigaArexxClientContract(unittest.TestCase):
    """Verify that AmigaArexxClient correctly implements ArexxClient."""

    def test_is_arexx_client(self):
        from doorforge.arexx.client import ArexxClient
        self.assertTrue(issubclass(AmigaArexxClient, ArexxClient))

    def test_has_call_method(self):
        client = AmigaArexxClient(node=1)
        self.assertTrue(hasattr(client, "call"))

    def test_has_close_method(self):
        client = AmigaArexxClient(node=1)
        self.assertTrue(hasattr(client, "close"))


if __name__ == "__main__":
    unittest.main()
