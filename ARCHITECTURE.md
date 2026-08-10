# uWatt Architecture

uWatt connects firmware context, electrical measurement and host-side analysis through
explicit boundaries.

```text
src/uwatt/cli             command-line frontend
src/uwatt/core            typed domain model and public facade
src/uwatt/config          schema loading and validation
src/uwatt/measurement     backend interface
src/uwatt/instruments     backend adapters
src/uwatt/events          firmware event parsing contracts
src/uwatt/correlation     event/sample synchronization
src/uwatt/analysis        electrical and temporal metrics
src/uwatt/diagnostics     diagnostic rule providers
src/uwatt/regression      baseline compatibility and comparison
src/uwatt/battery         workload and battery estimates
src/uwatt/reports         terminal, JSON, Markdown, HTML, JUnit
src/uwatt/boards          board profile loading
src/uwatt/artifacts       run artifact reading and writing
```

## Boundary Rules

- CLI handlers call library APIs. They do not own core behavior.
- Analysis consumes SI-normalized samples, events, regions and metrics.
- Instrument dependencies stay in instrument adapter packages and optional extras.
- Board knowledge is data-first and loaded from profiles.
- Diagnostics are emitted by providers and include evidence, confidence and remediation.
- Artifact schemas are versioned and validated.

## Data Flow

```text
Instrument backend
  -> SampleChunk and DigitalEvent streams
  -> artifact writer
  -> event correlation
  -> regions and power-state intervals
  -> metrics
  -> budgets, regression, diagnostics and battery model
  -> reports and machine-readable outputs
```

Checkpoint 0 implements the first permanent interfaces in this flow: core models, config
validation, the instrument contract and a synthetic backend.

## Measurement Contract

Each instrument implements:

```text
discover
open
configure
start
stream_samples
stream_digital_events
stop
close
capabilities
```

Samples use SI units before entering the core:

- timestamps in seconds;
- current in amperes;
- voltage in volts.

The backend reports capabilities explicitly. The core does not infer capabilities from
backend names.

## Configuration Contract

`uwatt.yaml` is validated by `schemas/config.schema.json`.

Unknown properties are rejected to avoid accepting invalid energy tests. Schema validation is
part of correctness because a misspelled budget can otherwise produce a false PASS.

## Artifact Contract

The manifest schema is `schemas/manifest.schema.json`. A run artifact records enough metadata
to reanalyze evidence later and to compare results only when experiments are compatible.

Raw evidence is retained separately from reports.

## Extensibility

Adding a backend should require implementing the measurement contract and registering or
exposing the backend. It must not require changes in analysis code.

Adding a board should require a board profile and documentation. It must not add conditionals
to shared metric calculation code.

Adding a diagnostic should add a provider or rule that consumes structured context and emits
structured findings.

