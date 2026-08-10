from __future__ import annotations

import copy
import unittest

from uwatt.config import ConfigurationError
from uwatt.config.schema import validate_config


class ManifestSchemaTest(unittest.TestCase):
    def test_minimal_manifest_validates(self) -> None:
        validate_config(_manifest(), "manifest.schema.json")

    def test_manifest_requires_run_id(self) -> None:
        manifest = _manifest()
        del manifest["run_id"]

        with self.assertRaisesRegex(ConfigurationError, "required property"):
            validate_config(manifest, "manifest.schema.json")


def _manifest() -> dict[str, object]:
    return copy.deepcopy(
        {
            "schema_version": "0.1",
            "uwatt_version": "0.1.0a0",
            "run_id": "run-001",
            "timestamp": "2026-08-10T16:00:00Z",
            "project": {"name": "env-sensor"},
            "scenario": {"name": "periodic_sensor"},
            "git": {"commit": "unknown", "branch": "unknown", "dirty": False},
            "firmware": {"image_hash": "unknown"},
            "platform": {"os": "Zephyr", "os_version": "unknown"},
            "target": {"board": "nrf52840dk/nrf52840", "mcu": "nRF52840"},
            "instrument": {"type": "synthetic", "serial": "synthetic"},
            "measurement": {
                "sample_rate": 1000.0,
                "supply_voltage": 3.0,
                "duration": 60.0,
            },
            "synchronization": {"method": "synthetic"},
            "environment": {"notes": "unit test"},
        }
    )


if __name__ == "__main__":
    unittest.main()
