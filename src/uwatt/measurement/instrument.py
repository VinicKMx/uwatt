"""Common measurement backend contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from uwatt.core.models import (
    DigitalEvent,
    InstrumentCapabilities,
    InstrumentDescriptor,
    MeasurementConfig,
    SampleChunk,
)


class Instrument(ABC):
    """Base class for all measurement instruments.

    Backend implementations normalize vendor-specific units before emitting
    ``SampleChunk`` or ``DigitalEvent`` objects.
    """

    @classmethod
    @abstractmethod
    def discover(cls) -> Sequence[InstrumentDescriptor]:
        """Return discoverable instruments for this backend."""

    @abstractmethod
    def open(self) -> None:
        """Open the instrument connection."""

    @abstractmethod
    def configure(self, config: MeasurementConfig) -> None:
        """Apply acquisition configuration."""

    @abstractmethod
    def start(self) -> None:
        """Start acquisition."""

    @abstractmethod
    def stream_samples(self) -> Iterable[SampleChunk]:
        """Yield SI-normalized sample chunks."""

    @abstractmethod
    def stream_digital_events(self) -> Iterable[DigitalEvent]:
        """Yield SI-normalized digital marker events."""

    @abstractmethod
    def stop(self) -> None:
        """Stop acquisition."""

    @abstractmethod
    def close(self) -> None:
        """Close the instrument connection."""

    @abstractmethod
    def capabilities(self) -> InstrumentCapabilities:
        """Return normalized backend capabilities."""

    def __enter__(self) -> Instrument:
        self.open()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


InstrumentConfiguration = Mapping[str, Any]
