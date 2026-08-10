# Architecture Layers

uWatt is organized into six permanent layers:

```text
CLI
Analysis
Measurement abstraction
Event correlation and synchronization
Firmware instrumentation
RTOS / MCU / board integration
```

Checkpoint 0 creates the package boundaries for these layers and documents the dependency
direction. Later checkpoints add implementation behind those boundaries.

