# OS Integration (Safe, Allowlisted)

OS actions are executed only by the OS adapter and always flow through the decision pipeline. The UI never executes OS calls directly.

## Adapter (Windows primary)
Implemented in `core/os_adapter.py`:
- `open_file(path)`
- `open_folder(path)`
- `launch_app(path, args)`
- `open_url(url)`
- `reveal_in_explorer(path)`
- **DRY_RUN** mode for tests

## App registry
Configuration file: `data/apps.json`
```json
{
  "apps": [
    {
      "app_id": "example_app",
      "name": "Example App",
      "path": "C:/Path/To/App.exe",
      "args": []
    }
  ]
}
```

## Pipeline flow
Intent → policy checks (overrides + confirmations) → adapter → events.
- Emits `OS_ACTION_REQUESTED | OS_ACTION_STARTED | OS_ACTION_FINISHED | OS_ACTION_FAILED | OS_ACTION_BLOCKED`.
- Uses the shared event schema (`docs/event_model.md`).

## Workspace launch sets
Optional launch items can be stored in workspace session data, but execution still follows overrides and confirmation rules.
