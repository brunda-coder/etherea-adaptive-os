# Etherea Final Merge Gate Verification

This document is the final human-visible verification path for merge readiness.

## Automated verification

Run the required checks:

```bash
python -m compileall .
python tools/etherea_feature_audit.py
python tools/etherea_runtime_selftest.py
```

Expected:
- `etherea_feature_audit.py` ends with `FAIL=0`.
- `etherea_runtime_selftest.py` ends with `SUMMARY failures=0`.
- Environment-only dependencies may be reported as `SKIP` (for example `libGL.so.1`/Playwright availability).

## Binary guard verification

The commit hook script must block new binaries outside curated asset roots and allow curated roots:
- `assets/**`
- `core/assets/**`
- `corund/assets/**`

To validate manually, stage a temporary `.png` file outside those roots and run:

```bash
scripts/prevent_binaries.sh
```

It should fail with a blocked-extension message. Then stage the same extension under an allowed root and rerun; it should pass.

## Manual desktop verification path (local machine)

Launch Etherea:

```bash
python main.py
```

Then verify all items below in one run:

1. **Avatar renders with real assets**
   - Avatar is visible at startup (not placeholder blocks).
2. **Speak Demo animation**
   - Open settings/privacy panel and click **Speak Demo**.
   - Confirm blink/breathe/mouth movement is visible while speaking.
3. **Tutorial overlay path**
   - Confirm tutorial overlay appears with **Next / Back / Skip**.
   - Click **Skip**, restart app, and confirm skip state persists.
4. **Workspace real actions**
   - **Drawing**: draw strokes and save.
   - **PDF**: open a PDF and run summarize/annotate action.
   - **Coding**: open/edit/save a file.
5. **Agent Works structured demo outputs**
   - In Agent Works panel, run:
     - `create_ppt`
     - `summarize_pdf`
     - `generate_notes`
   - Confirm each returns structured output (task/plan/steps/output fields).
6. **ESC kill switch**
   - Press `Esc` and confirm voice/sensors/adaptations/agent triggers pause.
7. **Settings visibility and functionality**
   - Confirm toggles and controls are present and functional for:
     - voice
     - mic
     - privacy
     - themes
     - connectors

## Environment-only limitations

If local environment lacks system libraries (for example `libGL.so.1`) or browser automation runtime (Playwright), classify as **ENV SKIP** and continue manual verification on a desktop with those dependencies installed.
