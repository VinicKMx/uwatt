# Run Artifact Format

Checkpoint 0 defines schemas but does not yet write `.uwatt` artifacts.

The intended logical layout is:

```text
run/
  manifest.json
  samples.parquet
  events.jsonl
  metrics.json
  diagnostics.json
  verdict.json
  report.html
  report.md
```

`schemas/manifest.schema.json` defines the manifest contract. Future checkpoints add the
artifact writer, reader and migration layer.

