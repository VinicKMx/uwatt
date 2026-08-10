from __future__ import annotations

import unittest

from uwatt.core import MeasurementConfig
from uwatt.instruments.synthetic import SyntheticInstrument


class SyntheticBackendTest(unittest.TestCase):
    def test_discovery_reports_capabilities_without_hardware(self) -> None:
        descriptors = SyntheticInstrument.discover()

        self.assertEqual(len(descriptors), 1)
        self.assertEqual(descriptors[0].backend, "synthetic")
        self.assertTrue(descriptors[0].capabilities.current_measurement)
        self.assertTrue(descriptors[0].capabilities.voltage_measurement)
        self.assertEqual(descriptors[0].capabilities.digital_inputs, 1)

    def test_capture_is_deterministic_and_si_normalized(self) -> None:
        first = _capture_currents()
        second = _capture_currents()

        self.assertEqual(first, second)
        self.assertIn(5e-6, first)
        self.assertIn(3e-3, first)
        self.assertIn(8e-3, first)

    def test_digital_events_mark_active_interval_boundaries(self) -> None:
        instrument = SyntheticInstrument(chunk_size=4)
        with instrument:
            instrument.configure(
                MeasurementConfig(
                    sample_rate_hz=1000.0,
                    supply_voltage_v=3.0,
                    duration_s=0.015,
                )
            )
            instrument.start()
            events = list(instrument.stream_digital_events())

        self.assertEqual(
            [(event.timestamp_s, event.value) for event in events],
            [(0.005, True), (0.01, False)],
        )


def _capture_currents() -> tuple[float, ...]:
    instrument = SyntheticInstrument(chunk_size=4)
    currents: list[float] = []
    with instrument:
        instrument.configure(
            MeasurementConfig(
                sample_rate_hz=1000.0,
                supply_voltage_v=3.0,
                duration_s=0.015,
            )
        )
        instrument.start()
        for chunk in instrument.stream_samples():
            currents.extend(chunk.current_a)
            if chunk.voltage_v is None:
                raise AssertionError("synthetic backend must emit voltage samples")
            self_voltages = set(chunk.voltage_v)
            if self_voltages != {3.0}:
                raise AssertionError(f"unexpected voltages: {self_voltages}")
    return tuple(currents)


if __name__ == "__main__":
    unittest.main()
