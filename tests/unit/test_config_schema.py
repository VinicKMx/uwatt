from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from uwatt.config import ConfigurationError, load_config, validate_config

ROOT = Path(__file__).resolve().parents[2]


class ConfigSchemaTest(unittest.TestCase):
    def test_example_configuration_validates(self) -> None:
        config = load_config(ROOT / "uwatt.yaml.example")

        self.assertEqual(config["project"]["name"], "env-sensor")
        self.assertIn("periodic_sensor", config["scenarios"])

    def test_unknown_top_level_property_is_rejected(self) -> None:
        config = _example_config()
        config["surprise"] = True

        with self.assertRaisesRegex(ConfigurationError, "Additional properties"):
            validate_config(config)

    def test_unknown_scenario_property_is_rejected(self) -> None:
        config = _example_config()
        config["scenarios"]["periodic_sensor"]["shell"] = "west flash"

        with self.assertRaisesRegex(ConfigurationError, "Additional properties"):
            validate_config(config)


def _example_config() -> dict[str, object]:
    with (ROOT / "uwatt.yaml.example").open("r", encoding="utf-8") as config_file:
        loaded = yaml.safe_load(config_file)
    if not isinstance(loaded, dict):
        raise AssertionError("example config did not load as a mapping")
    return copy.deepcopy(loaded)


if __name__ == "__main__":
    unittest.main()
