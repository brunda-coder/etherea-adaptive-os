# Deployment Readiness Update

## What was added
- `tools/etherea_doctor.py`: quick health report for Python/venv, imports, runtime capabilities, and asset resolution.
- `requirements-desktop.txt` and `requirements-dev.txt`: deterministic install split between runtime and developer tooling.
- `SETUP.md`: repeatable setup and sanity check commands for Windows/Linux.
- `.github/workflows/ci.yml`: CI checks for install, compile, doctor, and no-binaries policy.
- `scripts/install_hooks.py`: optional helper to install/remove a local pre-commit binary-blocking hook.
- `scripts/prevent_binaries.sh`: now supports `--range` for CI pull-request scans.

## Why
- Make setup reproducible across environments.
- Catch missing dependencies/assets early via one command.
- Enforce binary policy before merge.
- Keep runtime checks non-GUI and CI-safe.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-desktop.txt
python -m compileall .
python tools/etherea_doctor.py
bash scripts/prevent_binaries.sh --range "HEAD~1...HEAD"
```
