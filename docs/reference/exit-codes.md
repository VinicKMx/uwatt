# Exit Codes

uWatt CLI commands use stable exit codes:

```text
0 success
1 test or budget failure
2 invalid configuration
3 hardware or instrument unavailable
4 invalid experiment
5 analysis failure
6 incompatible baseline
```

CI integrations should use these codes instead of parsing terminal text. Commands that expose
machine-readable output should support JSON or another structured format.

