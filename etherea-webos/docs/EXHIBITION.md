# Exhibition Runbook

## One-command prototype run
```bash
cd etherea-webos && npm install && npm run build && npm run selfcheck
```

## Demo flow (laptop)
1. Open `apps/web` in browser with `npm run dev -w @etherea/web`.
2. Show boot aurora + tutorial, skip persistence.
3. Show avatar speak demo and diagnostics.
4. Switch through drawing/pdf/coding/agent/settings.

## Demo flow (phone)
1. Build APK via release workflow.
2. Install debug APK and run same flow.

## Existing desktop repository note
Legacy desktop paths remain untouched; this prototype is isolated under `etherea-webos/` for exhibition and release artifacts.
