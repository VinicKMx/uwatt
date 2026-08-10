from __future__ import annotations

import unittest

from uwatt.core import MeasurementConfig, MeasurementSession, Region, SampleChunk


class ModelValidationTest(unittest.TestCase):
    def test_sample_chunk_requires_equal_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "equal length"):
            SampleChunk(timestamps_s=(0.0, 0.1), current_a=(1e-3,))

    def test_sample_chunk_requires_monotonic_timestamps(self) -> None:
        with self.assertRaisesRegex(ValueError, "monotonically"):
            SampleChunk(timestamps_s=(0.1, 0.0), current_a=(1e-3, 1e-3))

    def test_region_duration_is_si_seconds(self) -> None:
        region = Region(name="sensor_read", start_s=1.0, end_s=1.25, source="test")

        self.assertAlmostEqual(region.duration_s, 0.25)

    def test_measurement_session_requires_identity(self) -> None:
        config = MeasurementConfig(
            sample_rate_hz=1000.0,
            supply_voltage_v=3.0,
            duration_s=1.0,
        )

        with self.assertRaisesRegex(ValueError, "session_id"):
            MeasurementSession(
                session_id="",
                instrument_backend="synthetic",
                instrument_identifier="synthetic:default",
                config=config,
            )


if __name__ == "__main__":
    unittest.main()
