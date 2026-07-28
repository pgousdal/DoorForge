import sys
import unittest
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from doorforge import ExecuteResult, ExitReason, Session
from doorforge.arexx import ArexxAdapter
from doorforge.arexx.client import (
    ArexxConnectionError,
    ArexxProtocolError,
    ArexxResult,
)
from doorforge.arexx.mock_client import MockArexxClient


def _default_session_responses(client: MockArexxClient) -> None:
    """Load a standard set of session-building responses."""
    client.expect("NODENUMBER", rc=0, result="1")
    client.expect("USERNAME", rc=0, result="Alice")
    client.expect("TIMELEFT", rc=0, result="1800")
    client.expect("GETCONSTAT", rc=0, result="0 NULL")
    client.expect("SYSOP", rc=1, result="")


# ---------------------------------------------------------------------------
# build_session tests
# ---------------------------------------------------------------------------


class TestArexxAdapterBuildSession(unittest.TestCase):
    """ArexxAdapter.build_session() tests."""

    def test_populates_all_supported_fields(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertIsInstance(session, Session)
        self.assertEqual(session.node_number, 1)
        self.assertEqual(session.display_name, "Alice")
        self.assertEqual(session.minutes_remaining, 30)  # 1800s / 60
        self.assertTrue(session.is_local)  # baud=0
        self.assertTrue(session.is_sysop)  # SYSOP RC=1

    def test_unsupported_user_id_is_none(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertIsNone(session.user_id)

    def test_unsupported_security_level_is_none(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertIsNone(session.security_level)

    def test_non_sysop_is_false(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("SYSOP", rc=0, result="")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertFalse(session.is_sysop)

    def test_remote_baud_detection(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("GETCONSTAT", rc=0, result="9600 MNP")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertFalse(session.is_local)

    def test_invalid_node_number_defaults_to_zero(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("NODENUMBER", rc=0, result="not-a-number")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertEqual(session.node_number, 0)

    def test_negative_timeleft_becomes_zero(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("TIMELEFT", rc=0, result="-10")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertEqual(session.minutes_remaining, 0)

    def test_missing_display_name_becomes_question_mark(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("USERNAME", rc=0, result="")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertEqual(session.display_name, "?")

    def test_connection_error_propagates(self):
        client = MockArexxClient()
        adapter = ArexxAdapter(client)

        with self.assertRaises(ArexxConnectionError):
            adapter.build_session()

    def test_calls_all_five_commands_in_order(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        adapter.build_session()

        commands = [call[0] for call in client.call_log]
        self.assertEqual(
            commands,
            ["NODENUMBER", "USERNAME", "TIMELEFT", "GETCONSTAT", "SYSOP"],
        )

    def test_session_validate_passes(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        session.validate()

    def test_sysop_rc_zero_produces_false(self):
        client = MockArexxClient()
        _default_session_responses(client)
        client.expect("SYSOP", rc=0, result="")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertFalse(session.is_sysop)

    def test_sysop_rc_one_produces_true(self):
        client = MockArexxClient()
        client.expect("NODENUMBER", rc=0, result="2")
        client.expect("USERNAME", rc=0, result="Bob")
        client.expect("TIMELEFT", rc=0, result="600")
        client.expect("GETCONSTAT", rc=0, result="0 NULL")
        client.expect("SYSOP", rc=1, result="")
        adapter = ArexxAdapter(client)

        session = adapter.build_session()

        self.assertTrue(session.is_sysop)


# ---------------------------------------------------------------------------
# execute tests
# ---------------------------------------------------------------------------


class TestArexxAdapterExecute(unittest.TestCase):
    """ArexxAdapter.execute() tests."""

    def test_rc_zero_returns_normal(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=0, result="")
        adapter = ArexxAdapter(client)
        output = StringIO()

        result = adapter.execute("test.ABBS", stdout=output)

        self.assertIsInstance(result, ExecuteResult)
        self.assertEqual(result.reason, ExitReason.NORMAL)
        self.assertEqual(result.raw_rc, 0)
        self.assertIn("Completed successfully", output.getvalue())

    def test_rc_twenty_returns_carrier_loss_or_timeout(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=20, result="")
        adapter = ArexxAdapter(client)
        output = StringIO()

        result = adapter.execute("test.ABBS", stdout=output)

        self.assertEqual(result.reason, ExitReason.CARRIER_LOSS_OR_TIMEOUT)
        self.assertEqual(result.raw_rc, 20)
        self.assertIn("Carrier lost or timeout", output.getvalue())

    def test_rc_five_returns_adapter_error(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=5, result="")
        adapter = ArexxAdapter(client)
        output = StringIO()

        result = adapter.execute("test.ABBS", stdout=output)

        self.assertEqual(result.reason, ExitReason.ADAPTER_ERROR)
        self.assertEqual(result.raw_rc, 5)

    def test_other_rc_returns_door_failure_with_raw_rc(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=42, result="")
        adapter = ArexxAdapter(client)

        result = adapter.execute("test.ABBS")

        self.assertEqual(result.reason, ExitReason.DOOR_FAILURE)
        self.assertEqual(result.raw_rc, 42)

    def test_execute_propagates_connection_error(self):
        client = MockArexxClient()
        adapter = ArexxAdapter(client)

        with self.assertRaises(ArexxConnectionError):
            adapter.execute("missing.ABBS")

    def test_on_output_callback(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=0, result="")
        adapter = ArexxAdapter(client)
        lines = []

        adapter.execute("test.ABBS", on_output=lines.append)

        self.assertGreater(len(lines), 0)
        self.assertTrue(any("Executing" in l for l in lines))

    def test_on_input_callback(self):
        client = MockArexxClient()
        client.expect("EXECUTE", rc=0, result="")
        adapter = ArexxAdapter(client)
        recorded = []

        def fake_input(prompt: str) -> str:
            recorded.append(prompt)
            return "y"

        adapter.execute("test.ABBS", on_input=fake_input)

        self.assertIsNotNone(fake_input)

    def test_close(self):
        client = MockArexxClient()
        _default_session_responses(client)
        adapter = ArexxAdapter(client)

        adapter.close()

        with self.assertRaises(ArexxConnectionError):
            adapter.build_session()

    def test_adapter_kind(self):
        client = MockArexxClient()
        adapter = ArexxAdapter(client)

        self.assertEqual(adapter.adapter_kind, "arexx")

    def test_raw_rc_preserved_across_all_reasons(self):
        client = MockArexxClient()
        adapter = ArexxAdapter(client)

        cases = [(0, ExitReason.NORMAL), (20, ExitReason.CARRIER_LOSS_OR_TIMEOUT)]
        for rc, expected_reason in cases:
            client.reset()
            client.expect("EXECUTE", rc=rc, result="")
            result = adapter.execute("test.ABBS")
            self.assertEqual(result.reason, expected_reason)
            self.assertEqual(result.raw_rc, rc)


# ---------------------------------------------------------------------------
# MockArexxClient tests
# ---------------------------------------------------------------------------


class TestMockArexxClient(unittest.TestCase):
    """MockArexxClient-specific tests."""

    def test_unknown_command_raises(self):
        client = MockArexxClient()

        with self.assertRaises(ArexxConnectionError):
            client.call("UNKNOWN")

    def test_call_log_records_commands(self):
        client = MockArexxClient()
        client.expect("NODENUMBER", rc=0, result="2")
        client.expect("USERNAME", rc=0, result="Bob")

        client.call("NODENUMBER")
        client.call("USERNAME", "extra")

        self.assertEqual(len(client.call_log), 2)
        self.assertEqual(client.call_log[0], ("NODENUMBER", ()))
        self.assertEqual(client.call_log[1], ("USERNAME", ("extra",)))

    def test_call_after_close_raises(self):
        client = MockArexxClient()
        client.expect("NODENUMBER", rc=0, result="1")
        client.close()

        with self.assertRaises(ArexxConnectionError):
            client.call("NODENUMBER")

    def test_reset_clears_log_and_expectations(self):
        client = MockArexxClient()
        client.expect("NODENUMBER", rc=0, result="1")

        client.call("NODENUMBER")
        self.assertEqual(len(client.call_log), 1)

        client.reset()
        self.assertEqual(client.call_log, [])

        with self.assertRaises(ArexxConnectionError):
            client.call("NODENUMBER")

        self.assertEqual(len(client.call_log), 1)

    def test_expect_carrier_loss(self):
        client = MockArexxClient()
        client.expect_carrier_loss("GETLINE")
        result = client.call("GETLINE")
        self.assertEqual(result.rc, 20)

    def test_expect_error(self):
        client = MockArexxClient()
        client.expect_error("TYPEFILE", rc=10, result="missing param")
        result = client.call("TYPEFILE")
        self.assertEqual(result.rc, 10)
        self.assertEqual(result.result, "missing param")


# ---------------------------------------------------------------------------
# ArexxResult tests
# ---------------------------------------------------------------------------


class TestArexxResult(unittest.TestCase):
    def test_frozen_dataclass(self):
        r = ArexxResult(rc=0, result="hello")
        self.assertEqual(r.rc, 0)
        self.assertEqual(r.result, "hello")

    def test_immutable(self):
        r = ArexxResult(rc=0, result="hello")
        with self.assertRaises(AttributeError):
            r.rc = 1  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ExecuteResult tests
# ---------------------------------------------------------------------------


class TestExecuteResult(unittest.TestCase):
    def test_default_raw_rc_is_none(self):
        r = ExecuteResult(reason=ExitReason.NORMAL)
        self.assertIsNone(r.raw_rc)

    def test_preserves_raw_rc(self):
        r = ExecuteResult(reason=ExitReason.CARRIER_LOSS_OR_TIMEOUT, raw_rc=20)
        self.assertEqual(r.raw_rc, 20)

    def test_immutable(self):
        r = ExecuteResult(reason=ExitReason.NORMAL)
        with self.assertRaises(AttributeError):
            r.reason = ExitReason.DOOR_FAILURE  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Session evidence-safe representation tests
# ---------------------------------------------------------------------------


class TestSessionEvidenceSafe(unittest.TestCase):
    """Verify that Session supports unavailable and optional fields."""

    def test_user_id_defaults_to_none(self):
        s = Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
        )
        self.assertIsNone(s.user_id)

    def test_security_level_defaults_to_none(self):
        s = Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
        )
        self.assertIsNone(s.security_level)

    def test_is_sysop_required(self):
        with self.assertRaises(TypeError):
            Session(  # type: ignore[call-arg]
                node_number=0, display_name="T", is_local=False, minutes_remaining=10
            )

    def test_user_id_none_passes_validation(self):
        Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
            user_id=None,
        ).validate()

    def test_security_level_none_passes_validation(self):
        Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
            security_level=None,
        ).validate()

    def test_user_id_zero_still_allowed(self):
        Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
            user_id=0,
        ).validate()

    def test_user_id_negative_raises(self):
        with self.assertRaises(ValueError):
            Session(
                node_number=0,
                display_name="T",
                is_local=False,
                minutes_remaining=10,
                is_sysop=False,
                user_id=-1,
            ).validate()

    def test_security_level_negative_raises(self):
        with self.assertRaises(ValueError):
            Session(
                node_number=0,
                display_name="T",
                is_local=False,
                minutes_remaining=10,
                is_sysop=False,
                security_level=-1,
            ).validate()

    def test_frozen_session(self):
        s = Session(
            node_number=0,
            display_name="T",
            is_local=False,
            minutes_remaining=10,
            is_sysop=False,
        )
        with self.assertRaises(AttributeError):
            s.node_number = 1  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
