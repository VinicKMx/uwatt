# Security and Safety

uWatt controls and observes hardware. Safety issues include both software security defects and
unsafe hardware-control behavior.

## Report a Vulnerability

Until a dedicated security contact exists, open a private security advisory in the repository
or contact the maintainers directly.

Include:

- affected version or commit;
- reproduction steps;
- expected impact;
- whether hardware voltage, flashing or external equipment is involved.

## Hardware Safety Boundaries

- Programmable supply voltage must be checked against board and instrument limits.
- Automatic flashing must target explicitly selected hardware.
- Scenario files must not accept arbitrary shell commands.
- Infrastructure failures must not be reported as energy regressions.
- Unsafe or unsupported voltage values must be rejected before hardware is configured.

