# Configuration Reference

Primary configuration lives in `uwatt.yaml` and is validated by
`schemas/config.schema.json`.

Checkpoint 0 supports the structural contract:

- `project.name`;
- `target.board`;
- `instrument.backend`;
- `instrument.voltage`;
- `synchronization.method`;
- `scenarios.<name>.duration`;
- `scenarios.<name>.repetitions`;
- optional expectations and budgets.

Unknown properties are rejected by default.

Validate an example:

```console
uwatt validate-config uwatt.yaml.example
```

