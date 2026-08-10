# uWatt

Embedded energy observability and regression testing.

Measure where firmware spends energy, correlate current with code, detect low-power problems,
and prevent energy regressions in CI.

```console
$ uwatt validate-config uwatt.yaml.example
PASS  configuration valid: uwatt.yaml.example

$ uwatt devices
uWatt Devices
  synthetic:default  uWatt deterministic synthetic instrument
```

uWatt connects firmware context, real electrical measurement and host-side analysis so an
embedded engineer can answer:

- which firmware operation consumed charge or energy;
- whether a low-power state was actually reached;
- whether wakeups or devices explain unexpected current;
- whether a change introduced an energy regression;
- whether a declared energy budget is satisfied.

## Project Status

This repository is at checkpoint 0: product contract and repository foundation.

Implemented now:

- Python package skeleton and public `uwatt.Session` facade;
- typed core domain objects;
- measurement backend contract;
- deterministic synthetic instrument backend;
- strict JSON schemas for project config, manifest, metrics and diagnostics;
- CLI commands for config validation, synthetic device discovery and board profile listing;
- board profiles as data for Nordic, Espressif and STM32 reference targets;
- unit and integration tests that require no hardware;
- CI definition for formatting, linting, type checking and tests;
- architecture and reference documentation.

Later checkpoints add artifact storage, firmware correlation, analysis, Zephyr integration,
real instruments, budgets, regression testing, diagnostics, battery modeling and reports.

## Install

For local development:

```console
python3 -m pip install -e ".[dev]"
```

For a hardware-free smoke test without installing the package:

```console
PYTHONPATH=src python3 -m uwatt validate-config uwatt.yaml.example
```

## Test

```console
make test
```

The base test suite uses the synthetic backend and does not require a measurement instrument,
debug probe or target board.

## Architecture

uWatt is structured as six cooperating layers:

```text
uWatt CLI
Analysis engine
Measurement abstraction
Event correlation and synchronization
Firmware instrumentation
RTOS / MCU / board integration
```

Vendor-specific behavior belongs behind adapters. Analysis, budgets, reports and battery
calculations consume normalized SI-unit data and typed domain objects, not instrument-specific
payloads.

See [ARCHITECTURE.md](ARCHITECTURE.md) and [PROJECT_SPEC.md](PROJECT_SPEC.md).

## Supported Reference Targets

Checkpoint 0 defines data profiles for the intended reference matrix:

- Nordic nRF52840 DK under Zephyr;
- Espressif ESP32-C3-DevKitM under Zephyr;
- ST NUCLEO-U575ZI-Q under Zephyr.

The profiles document measurement connection assumptions and caveats. They do not place
board-specific logic in the analysis core.

## Buy Me a Coffee

If this project helped you, you can send a few sats over Lightning:

`maquinalab@walletofsatoshi.com`

<img src="assets/lightning-donation-qr.svg" alt="Lightning donation QR code" width="180">

## License

Apache-2.0. See [LICENSE](LICENSE).
