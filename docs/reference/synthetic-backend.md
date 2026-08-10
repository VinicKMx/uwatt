# Synthetic Backend

The synthetic backend is deterministic and requires no hardware.

It implements the measurement instrument contract and emits:

- timestamps in seconds;
- current in amperes;
- voltage in volts;
- one digital marker channel.

The default trace alternates sleep, active, sensor spike and sleep segments. It exists to test
CLI, schemas, future artifact writing, analysis and reporting without a connected board or
power instrument.

