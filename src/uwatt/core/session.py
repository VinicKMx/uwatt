"""Public session facade.

Checkpoint 0 establishes the boundary: CLI commands and Python consumers use
this facade instead of reaching into backend-specific implementation details.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Session:
    """Top-level library facade for a uWatt project configuration."""

    config: Mapping[str, Any]

    def run(self, scenario_name: str) -> None:
        """Run a scenario.

        Scenario execution is intentionally not implemented in checkpoint 0.
        The permanent API entrypoint exists so later checkpoints can add
        behavior without moving orchestration into CLI handlers.
        """

        raise NotImplementedError(f"scenario execution is not implemented yet: {scenario_name}")
