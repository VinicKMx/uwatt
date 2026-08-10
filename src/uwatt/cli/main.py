"""uWatt command-line interface."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from uwatt import __version__
from uwatt.config import ConfigurationError, load_config
from uwatt.core import exit_codes
from uwatt.instruments.synthetic import SyntheticInstrument


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uwatt",
        description="Embedded energy observability and regression testing.",
    )
    parser.add_argument("--version", action="store_true", help="show uWatt version and exit")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate-config",
        help="validate a uwatt.yaml project configuration",
    )
    validate_parser.add_argument("path", nargs="?", default="uwatt.yaml")
    validate_parser.add_argument("--format", choices=["terminal", "json"], default="terminal")

    devices_parser = subparsers.add_parser("devices", help="list measurement instruments")
    devices_parser.add_argument("--backend", choices=["synthetic"], default="synthetic")
    devices_parser.add_argument("--format", choices=["terminal", "json"], default="terminal")

    boards_parser = subparsers.add_parser("boards", help="list bundled board profiles")
    boards_parser.add_argument("--format", choices=["terminal", "json"], default="terminal")

    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return exit_codes.SUCCESS

    if args.command == "validate-config":
        return _validate_config(Path(args.path), args.format)
    if args.command == "devices":
        return _devices(args.format)
    if args.command == "boards":
        return _boards(args.format)

    parser.print_help()
    return exit_codes.SUCCESS


def _validate_config(path: Path, output_format: str) -> int:
    try:
        load_config(path)
    except (ConfigurationError, OSError) as exc:
        payload = {"status": "invalid", "path": str(path), "error": str(exc)}
        _print_payload(payload, output_format)
        return exit_codes.INVALID_CONFIGURATION

    payload = {"status": "valid", "path": str(path)}
    _print_payload(payload, output_format)
    return exit_codes.SUCCESS


def _devices(output_format: str) -> int:
    devices = [
        {
            "backend": descriptor.backend,
            "identifier": descriptor.identifier,
            "display_name": descriptor.display_name,
            "capabilities": {
                "current_measurement": descriptor.capabilities.current_measurement,
                "voltage_measurement": descriptor.capabilities.voltage_measurement,
                "programmable_supply": descriptor.capabilities.programmable_supply,
                "digital_inputs": descriptor.capabilities.digital_inputs,
                "hardware_trigger": descriptor.capabilities.hardware_trigger,
                "max_sample_rate_hz": descriptor.capabilities.max_sample_rate_hz,
                "device_serial": descriptor.capabilities.device_serial,
            },
        }
        for descriptor in SyntheticInstrument.discover()
    ]
    _print_payload({"devices": devices}, output_format)
    return exit_codes.SUCCESS


def _boards(output_format: str) -> int:
    root = Path(__file__).resolve().parents[3]
    profiles = sorted(str(path.relative_to(root)) for path in (root / "boards").glob("*/*.yaml"))
    _print_payload({"board_profiles": profiles}, output_format)
    return exit_codes.SUCCESS


def _print_payload(payload: Mapping[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    status = payload.get("status")
    if status == "valid":
        print(f"PASS  configuration valid: {payload['path']}")
    elif status == "invalid":
        print(f"FAIL  configuration invalid: {payload['path']}")
        print(f"      {payload['error']}")
    elif "devices" in payload:
        print("uWatt Devices")
        for device in payload["devices"]:
            print(f"  {device['identifier']}  {device['display_name']}")
    elif "board_profiles" in payload:
        print("uWatt Board Profiles")
        for profile in payload["board_profiles"]:
            print(f"  {profile}")
