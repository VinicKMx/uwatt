"""Schema loading and validation for uWatt project configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class ConfigurationError(ValueError):
    """Raised when a configuration document is invalid."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def schema_path(schema_name: str) -> Path:
    """Return the repository schema path for a known schema file."""

    candidates = [
        Path.cwd() / "schemas" / schema_name,
        _repo_root() / "schemas" / schema_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"schema not found: {schema_name}")


def load_schema(schema_name: str = "config.schema.json") -> dict[str, Any]:
    """Load a JSON schema by file name."""

    with schema_path(schema_name).open("r", encoding="utf-8") as schema_file:
        loaded = json.load(schema_file)
    if not isinstance(loaded, dict):
        raise ConfigurationError(f"schema must be an object: {schema_name}")
    return loaded


def validate_config(config: dict[str, Any], schema_name: str = "config.schema.json") -> None:
    """Validate a configuration mapping against a uWatt JSON schema."""

    schema = load_schema(schema_name)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    errors = sorted(validator.iter_errors(config), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ConfigurationError(f"{location}: {first.message}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a YAML or JSON uWatt configuration file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as config_file:
        suffixes = {suffix.lower() for suffix in config_path.suffixes}
        if suffixes.intersection({".yaml", ".yml"}):
            loaded = yaml.safe_load(config_file)
        else:
            loaded = json.load(config_file)

    if not isinstance(loaded, dict):
        raise ConfigurationError("configuration root must be a mapping")
    validate_config(loaded)
    return loaded
