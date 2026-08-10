# Contributing to uWatt

uWatt is intended to be a production-quality embedded energy observability project. Changes
should preserve explicit interfaces, reproducibility and evidence-based reporting.

## Development Setup

```console
python3 -m pip install -e ".[dev]"
```

## Checks

Base tests require no hardware:

```console
make test
```

Full local checks:

```console
make check
```

CI runs formatting, linting, type checking and tests.

## Engineering Standards

- Keep vendor-specific behavior behind adapters.
- Keep analysis code independent from instrument backends and board names.
- Validate schemas before converting configuration to typed models.
- Store physical units internally as SI values.
- Preserve raw evidence when implementing artifact-producing behavior.
- Mark hardware tests separately from the default test suite.
- Add or update documentation when changing public behavior.

## Documentation

`PROJECT_SPEC.md` is authoritative. If a change disagrees with it, update the specification or
the implementation explicitly in the same review.

Important design choices should update `PROJECT_SPEC.md`, `ARCHITECTURE.md` or the relevant
public reference documentation.

## Hardware Safety

Any code that controls programmable supplies, flashing or reset lines must validate explicit
board and instrument limits. Scenario files must not execute arbitrary shell commands.
