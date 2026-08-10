"""Deterministic synthetic measurement backend.

The synthetic backend is a real implementation of the measurement contract and
is deliberately hardware-free. It is used by tests, examples and future CLI
demos to exercise uWatt's pipeline before physical instruments are connected.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import ceil

from uwatt.core.models import (
    DigitalEvent,
    InstrumentCapabilities,
    InstrumentDescriptor,
    MeasurementConfig,
    SampleChunk,
)
from uwatt.measurement.instrument import Instrument


@dataclass(frozen=True)
class SyntheticStep:
    """A constant-current segment in a deterministic synthetic waveform."""

    duration_s: float
    current_a: float
    label: str


class SyntheticInstrument(Instrument):
    """Hardware-free instrument that emits a repeatable active/sleep trace."""

    BACKEND = "synthetic"
    IDENTIFIER = "synthetic:default"
    DEFAULT_SAMPLE_RATE_HZ = 1_000.0
    DEFAULT_SUPPLY_VOLTAGE_V = 3.0
    DEFAULT_PATTERN: tuple[SyntheticStep, ...] = (
        SyntheticStep(duration_s=0.005, current_a=5e-6, label="sleep"),
        SyntheticStep(duration_s=0.003, current_a=3e-3, label="active"),
        SyntheticStep(duration_s=0.002, current_a=8e-3, label="sensor_spike"),
        SyntheticStep(duration_s=0.005, current_a=5e-6, label="sleep"),
    )

    def __init__(
        self,
        *,
        pattern: Sequence[SyntheticStep] | None = None,
        chunk_size: int = 128,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self._pattern = tuple(pattern or self.DEFAULT_PATTERN)
        if not self._pattern:
            raise ValueError("pattern must contain at least one step")
        self._chunk_size = chunk_size
        self._config = MeasurementConfig(
            sample_rate_hz=self.DEFAULT_SAMPLE_RATE_HZ,
            supply_voltage_v=self.DEFAULT_SUPPLY_VOLTAGE_V,
            duration_s=sum(step.duration_s for step in self._pattern),
        )
        self._opened = False
        self._started = False

    @classmethod
    def discover(cls) -> Sequence[InstrumentDescriptor]:
        return (
            InstrumentDescriptor(
                backend=cls.BACKEND,
                identifier=cls.IDENTIFIER,
                display_name="uWatt deterministic synthetic instrument",
                capabilities=cls._capabilities(),
            ),
        )

    @classmethod
    def _capabilities(cls) -> InstrumentCapabilities:
        return InstrumentCapabilities(
            current_measurement=True,
            voltage_measurement=True,
            programmable_supply=False,
            digital_inputs=1,
            hardware_trigger=True,
            max_sample_rate_hz=100_000.0,
            device_serial="synthetic",
            metadata={"deterministic": True},
        )

    def open(self) -> None:
        self._opened = True

    def configure(self, config: MeasurementConfig) -> None:
        self._config = config

    def start(self) -> None:
        if not self._opened:
            raise RuntimeError("instrument must be opened before start")
        self._started = True

    def stream_samples(self) -> Iterable[SampleChunk]:
        if not self._started:
            raise RuntimeError("instrument must be started before streaming samples")

        total_samples = max(1, ceil(self._config.duration_s * self._config.sample_rate_hz))
        timestamps: list[float] = []
        currents: list[float] = []
        voltages: list[float] = []

        for sample_index in range(total_samples):
            timestamp_s = sample_index / self._config.sample_rate_hz
            timestamps.append(timestamp_s)
            currents.append(self._current_at(timestamp_s))
            voltages.append(self._config.supply_voltage_v)

            if len(timestamps) == self._chunk_size:
                yield SampleChunk(
                    timestamps_s=tuple(timestamps),
                    current_a=tuple(currents),
                    voltage_v=tuple(voltages),
                    metadata={"backend": self.BACKEND},
                )
                timestamps.clear()
                currents.clear()
                voltages.clear()

        if timestamps:
            yield SampleChunk(
                timestamps_s=tuple(timestamps),
                current_a=tuple(currents),
                voltage_v=tuple(voltages),
                metadata={"backend": self.BACKEND},
            )

    def stream_digital_events(self) -> Iterable[DigitalEvent]:
        if not self._started:
            raise RuntimeError("instrument must be started before streaming events")

        elapsed_s = 0.0
        marker_high = False
        for step in self._pattern:
            if elapsed_s > self._config.duration_s:
                return
            is_active = step.label != "sleep"
            if is_active != marker_high:
                marker_high = is_active
                yield DigitalEvent(
                    timestamp_s=elapsed_s,
                    channel=0,
                    value=marker_high,
                    metadata={"label": step.label},
                )
            elapsed_s += step.duration_s
        if marker_high and elapsed_s <= self._config.duration_s:
            yield DigitalEvent(
                timestamp_s=elapsed_s,
                channel=0,
                value=False,
                metadata={"label": "sleep"},
            )

    def stop(self) -> None:
        self._started = False

    def close(self) -> None:
        self._started = False
        self._opened = False

    def capabilities(self) -> InstrumentCapabilities:
        return self._capabilities()

    def _current_at(self, timestamp_s: float) -> float:
        period_s = sum(step.duration_s for step in self._pattern)
        offset_s = timestamp_s % period_s
        elapsed_s = 0.0
        for step in self._pattern:
            elapsed_s += step.duration_s
            if offset_s < elapsed_s:
                return step.current_a
        return self._pattern[-1].current_a
