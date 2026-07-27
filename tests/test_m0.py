import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from doorforge import Session


class M0Tests(unittest.TestCase):
    def test_inventory_identity(self):
        data = json.loads(
            (ROOT / "reference/abbs320-inventory.json").read_text(encoding="utf-8")
        )
        self.assertEqual(data["entry_count"], 222)
        self.assertEqual(
            data["source_sha256"],
            "5e9fd4cbf871a2bbd4579a3f9b35a0cd2187676cab8886b16adbfe8b038380e4",
        )

    def test_key_abbs_surfaces_exist(self):
        data = json.loads(
            (ROOT / "reference/abbs320-inventory.json").read_text(encoding="utf-8")
        )
        paths = {entry["path"] for entry in data["entries"]}
        expected = {
            "ABBS/Docs/Doors.doc",
            "ABBS/Docs/abbsrexx.doc",
            "ABBS/Docs/abbsrexx.guide",
            "ABBS/Doors/DAYS/DAYS.ABBS",
            "ABBS/Doors/DAYS/DAYS.DOC",
            "ABBS/Doors/Node0Config",
            "ABBS/Doors/Node0Menu",
        }
        self.assertTrue(expected.issubset(paths))

    def test_session_validation(self):
        Session(
            user_id=1,
            node_number=0,
            security_level=10,
            minutes_remaining=30,
            is_local=False,
            display_name="Test User",
        ).validate()

    def test_hello_door(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "examples/hello-door/hello_door.py"),
                "--user",
                "ABBS Tester",
                "--node",
                "1",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Welcome, ABBS Tester!", result.stdout)
        self.assertIn("Node: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
