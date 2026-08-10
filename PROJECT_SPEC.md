# uWatt Project Specification

This file is the normative product specification for uWatt. When README text,
implementation behavior or documentation disagree with this file, the disagreement must be
resolved explicitly.

## Mission

uWatt makes energy behavior a measurable, explainable and testable property of embedded
firmware.

The project correlates firmware intent, firmware events, electrical measurements and
host-side analysis so engineers can understand where energy went, whether the result is
acceptable, what may be wrong and whether a change caused an energy regression.

## Scope

uWatt observes, measures, correlates, diagnoses and verifies energy behavior. It is not a
replacement for Zephyr power management, an oscilloscope application, a battery chemistry
simulator, a BLE stack or a collection of board-specific scripts.

The permanent product pipeline is:

```text
firmware intent
semantic instrumentation
real electrical measurement
synchronized evidence
quantitative analysis
engineering diagnostics
energy requirements
regression protection
```

Every major feature should reinforce this pipeline.

## Terminology

- Sample: one measured electrical observation.
- Capture: raw acquisition over a time interval.
- Event: instantaneous semantic marker.
- Region: time interval with semantic meaning.
- Scenario: declarative reproducible experiment.
- Run: one execution of a scenario.
- Metric: calculated quantitative result.
- Budget: absolute acceptance requirement.
- Baseline: approved reference measurement.
- Regression: meaningful deterioration relative to a baseline.
- Diagnostic: explanation or probable issue derived from evidence.
- Artifact: portable stored representation of a run.

## Architecture Contract

uWatt has six layers:

```text
CLI
Analysis
Measurement abstraction
Event correlation and synchronization
Firmware instrumentation
RTOS / MCU / board integration
```

Each layer exposes an explicit interface. Vendor-specific behavior remains behind adapters.
Analysis code must not depend directly on Joulescope, PPK2, Zephyr board names or other
backend-specific payloads.

Internally, calculations use SI units:

- current: ampere;
- voltage: volt;
- time: second;
- charge: coulomb;
- energy: joule;
- power: watt.

Human-readable formatters may choose `mA`, `uA`, `uC`, `uJ`, `ms` and related display units,
but calculations must not depend on formatted strings.

## Central Domain Objects

The public model includes:

- `MeasurementSession`;
- `Instrument`;
- `InstrumentCapabilities`;
- `SampleChunk`;
- `DigitalEvent`;
- `FirmwareEvent`;
- `Region`;
- `PowerStateInterval`;
- `Metric`;
- `Scenario`;
- `Budget`;
- `Diagnostic`;
- `RunManifest`;
- `Baseline`;
- `Comparison`;
- `BatteryModel`;
- `Report`.

Configuration may originate as YAML or JSON, but core behavior consumes validated typed
objects rather than passing unstructured dictionaries through the system.

## Measurement Backends

Backends implement the common contract:

```text
discover()
open()
configure()
start()
stream_samples()
stream_digital_events()
stop()
close()
capabilities()
```

Required backend families are:

- synthetic;
- file/import;
- Joulescope;
- Nordic PPK2.

The synthetic backend is required to be deterministic and hardware-free so CLI, artifact,
analysis, budget, report and regression logic can be tested without physical equipment.

## Configuration

Project configuration is stored in `uwatt.yaml` and validated against
`schemas/config.schema.json`.

Unknown properties are normally rejected. This is deliberate: silent acceptance of misspelled
measurement, synchronization or budget fields can produce invalid engineering evidence.

Scenario files must not accept arbitrary shell commands as a convenience mechanism.
Execution actions must be constrained and explicit.

## Run Artifact

Every physical experiment produces a portable run artifact with a documented manifest.
The canonical logical structure is:

```text
run/
  manifest.json
  samples.parquet
  events.jsonl
  metrics.json
  diagnostics.json
  verdict.json
  report.html
  report.md
```

The packable `.uwatt` representation is versioned. Older artifacts should remain readable
through explicit schema migration after reasonable future releases.

## CLI Guarantees

Primary commands are:

```text
uwatt init
uwatt devices
uwatt boards
uwatt doctor
uwatt run
uwatt capture
uwatt analyze
uwatt test
uwatt compare
uwatt baseline
uwatt battery
uwatt report
uwatt inspect
```

Checkpoint 0 implements only the foundation commands needed to validate the contract:
`validate-config`, `devices` for the synthetic backend and `boards`.

Stable exit codes:

```text
0 success
1 test or budget failure
2 invalid configuration
3 hardware or instrument unavailable
4 invalid experiment
5 analysis failure
6 incompatible baseline
```

Machine-readable output is required for relevant CLI operations.

## Quality Requirements

The base test suite must run without hardware. Hardware tests are separately marked because
normal contributors may not own the equipment.

Measurement verdicts must distinguish:

- infrastructure failure;
- firmware or experiment failure;
- invalid measurement;
- budget failure;
- regression failure.

Invalid or low-quality evidence must not be reported as PASS.

## Reference Platform Matrix

The final reference implementation demonstrates three Zephyr MCU ecosystems:

- Nordic nRF52840 DK;
- Espressif ESP32-C3-DevKitM;
- ST NUCLEO-U575ZI-Q.

Reference profiles are data. The analysis core must not contain copy-pasted board-specific
pipelines.

## Checkpoint Status

Checkpoint 0 establishes product contract and repository foundation. It is complete when:

- repository installs cleanly;
- tests execute with one documented command;
- configuration is schema validated;
- architecture boundaries are documented;
- no hardware dependency is required to run the base test suite;
- synthetic backend contract exists;
- CI validates formatting, static checks and tests;
- this file is present and authoritative.

Later checkpoints build permanent functionality on top of this foundation; they must not
introduce disposable public APIs or temporary artifact formats.

