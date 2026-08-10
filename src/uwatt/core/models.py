"""Typed domain objects shared by the library and CLI.

These models intentionally keep hardware-vendor details out of the analysis
surface. Configuration loaders may start with YAML or JSON, but core code
should consume typed objects like these rather than unstructured dictionaries.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from typing import Any


def _require_finite(name: str, value: float) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True)
class InstrumentCapabilities:
    """Normalized capabilities reported by a measurement backend."""

    current_measurement: bool
    voltage_measurement: bool
    programmable_supply: bool
    digital_inputs: int
    hardware_trigger: bool
    max_sample_rate_hz: float | None = None
    device_serial: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.digital_inputs < 0:
            raise ValueError("digital_inputs must be non-negative")
        if self.max_sample_rate_hz is not None:
            _require_finite("max_sample_rate_hz", self.max_sample_rate_hz)
            if self.max_sample_rate_hz <= 0:
                raise ValueError("max_sample_rate_hz must be positive")


@dataclass(frozen=True)
class InstrumentDescriptor:
    """A discoverable instrument without an open session."""

    backend: str
    identifier: str
    display_name: str
    capabilities: InstrumentCapabilities


@dataclass(frozen=True)
class MeasurementConfig:
    """Configuration for one acquisition."""

    sample_rate_hz: float
    supply_voltage_v: float
    duration_s: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_finite("sample_rate_hz", self.sample_rate_hz)
        _require_finite("supply_voltage_v", self.supply_voltage_v)
        _require_finite("duration_s", self.duration_s)
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if self.supply_voltage_v <= 0:
            raise ValueError("supply_voltage_v must be positive")
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")


@dataclass(frozen=True)
class MeasurementSession:
    """Identity and configuration for one measurement acquisition."""

    session_id: str
    instrument_backend: str
    instrument_identifier: str
    config: MeasurementConfig
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("session_id must not be empty")
        if not self.instrument_backend:
            raise ValueError("instrument_backend must not be empty")
        if not self.instrument_identifier:
            raise ValueError("instrument_identifier must not be empty")


@dataclass(frozen=True)
class SampleChunk:
    """A streaming chunk of SI-normalized electrical samples."""

    timestamps_s: Sequence[float]
    current_a: Sequence[float]
    voltage_v: Sequence[float] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        sample_count = len(self.timestamps_s)
        if sample_count == 0:
            raise ValueError("SampleChunk must contain at least one sample")
        if len(self.current_a) != sample_count:
            raise ValueError("timestamps_s and current_a must have equal length")
        if self.voltage_v is not None and len(self.voltage_v) != sample_count:
            raise ValueError("voltage_v must match timestamps_s length")

        previous: float | None = None
        for index, timestamp_s in enumerate(self.timestamps_s):
            _require_finite(f"timestamps_s[{index}]", timestamp_s)
            if previous is not None and timestamp_s < previous:
                raise ValueError("timestamps_s must be monotonically non-decreasing")
            previous = timestamp_s
        for index, current_a in enumerate(self.current_a):
            _require_finite(f"current_a[{index}]", current_a)
        if self.voltage_v is not None:
            for index, voltage_v in enumerate(self.voltage_v):
                _require_finite(f"voltage_v[{index}]", voltage_v)

    @property
    def start_s(self) -> float:
        return self.timestamps_s[0]

    @property
    def end_s(self) -> float:
        return self.timestamps_s[-1]


@dataclass(frozen=True)
class DigitalEvent:
    """A timestamped digital marker edge or level sample."""

    timestamp_s: float
    channel: int
    value: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_finite("timestamp_s", self.timestamp_s)
        if self.channel < 0:
            raise ValueError("channel must be non-negative")


class FirmwareEventKind(StrEnum):
    EVENT = "event"
    REGION_BEGIN = "region_begin"
    REGION_END = "region_end"
    STATE = "state"
    COUNTER = "counter"
    VALUE = "value"


@dataclass(frozen=True)
class FirmwareEvent:
    """A semantic firmware marker after transport parsing."""

    timestamp_s: float
    kind: FirmwareEventKind
    name: str
    value: float | str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_finite("timestamp_s", self.timestamp_s)
        if not self.name:
            raise ValueError("name must not be empty")


@dataclass(frozen=True)
class Region:
    """A semantic interval, usually derived from firmware events."""

    name: str
    start_s: float
    end_s: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        _require_finite("start_s", self.start_s)
        _require_finite("end_s", self.end_s)
        if self.end_s < self.start_s:
            raise ValueError("end_s must be greater than or equal to start_s")

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


@dataclass(frozen=True)
class PowerStateInterval:
    """A classified power-behavior interval with confidence metadata."""

    classification: str
    start_s: float
    end_s: float
    confidence: str
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Metric:
    """A calculated SI-unit metric."""

    name: str
    value: float
    unit: str
    subject: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        _require_finite("value", self.value)
        if not self.unit:
            raise ValueError("unit must not be empty")


@dataclass(frozen=True)
class Budget:
    """An absolute requirement evaluated against metrics."""

    subject: str
    metric: str
    maximum: float | None = None
    minimum: float | None = None
    unit: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    """A declarative experiment after schema validation."""

    name: str
    board: str
    duration_s: float
    repetitions: int = 1
    budgets: Sequence[Budget] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        _require_finite("duration_s", self.duration_s)
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        if self.repetitions <= 0:
            raise ValueError("repetitions must be positive")


class DiagnosticSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Diagnostic:
    """Evidence-backed diagnostic finding."""

    rule_id: str
    severity: DiagnosticSeverity
    confidence: str
    evidence: str
    explanation: str
    remediation: str
    platform: str | None = None
    documentation_url: str | None = None


@dataclass(frozen=True)
class RunManifest:
    """Portable metadata for a uWatt run artifact."""

    schema_version: str
    uwatt_version: str
    run_id: str
    timestamp: str
    project: Mapping[str, Any]
    scenario: Mapping[str, Any]
    git: Mapping[str, Any]
    firmware: Mapping[str, Any]
    platform: Mapping[str, Any]
    target: Mapping[str, Any]
    instrument: Mapping[str, Any]
    measurement: Mapping[str, Any]
    synchronization: Mapping[str, Any]
    environment: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Baseline:
    """Approved reference data used for regression checks."""

    name: str
    manifest: RunManifest
    metrics: Sequence[Metric]


@dataclass(frozen=True)
class Comparison:
    """A baseline-to-current comparison result."""

    baseline: str
    current: str
    metrics: Sequence[Metric]
    compatible: bool
    verdict: str


@dataclass(frozen=True)
class BatteryModel:
    """Battery workload assumptions and derived summary."""

    name: str
    assumptions: Mapping[str, Any]
    metrics: Sequence[Metric]


@dataclass(frozen=True)
class Report:
    """A generated report descriptor."""

    run_id: str
    format: str
    path: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
