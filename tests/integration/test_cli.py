from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path

from uwatt.cli.main import main
from uwatt.core import exit_codes

ROOT = Path(__file__).resolve().parents[2]


class CliTest(unittest.TestCase):
    def test_validate_config_json_output(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "validate-config",
                    str(ROOT / "uwatt.yaml.example"),
                    "--format",
                    "json",
                ]
            )

        self.assertEqual(exit_code, exit_codes.SUCCESS)
        self.assertIn('"status": "valid"', stdout.getvalue())

    def test_devices_lists_synthetic_backend(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(["devices"])

        self.assertEqual(exit_code, exit_codes.SUCCESS)
        self.assertIn("synthetic:default", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
