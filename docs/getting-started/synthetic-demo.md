# Synthetic Demo

The synthetic backend is the first runnable demonstration because it requires no hardware.

```console
python3 -m pip install -e .
uwatt validate-config uwatt.yaml.example
uwatt devices
make test
```

Future checkpoints will extend this into `uwatt run` and report generation.

