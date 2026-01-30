# Event Spine

All subsystems communicate through a single event schema. This keeps logging consistent across UI, Aurora, avatar, and OS integrations.

## Event schema
- **type**: event name (`TTS_STARTED`, `ACTION_FINISHED`, `OS_ACTION_BLOCKED`, ...).
- **timestamp**: ISO-8601 UTC time.
- **source**: emitting subsystem (`voice_engine`, `aurora_pipeline`, `os_pipeline`, ...).
- **payload**: structured event detail.
- **priority**: integer priority (default `50`).
- **privacy_level**: `normal | sensitive`.

## Reference implementation
See `core/event_model.py` and `core/event_bus.py`.

## Example
```json
{
  "type": "OS_ACTION_STARTED",
  "timestamp": "2026-01-26T09:15:45Z",
  "source": "os_pipeline",
  "payload": {
    "intent": "OPEN_FOLDER",
    "path": "workspace"
  },
  "priority": 35,
  "privacy_level": "normal"
}
```
# Etherea Internal Event Model

## Purpose
A single internal event message shape used across UI, engine, CLI, voice, and sensors. This is documentation only; it does not change runtime behavior.

## Event Shape
```json
{
  "id": "evt_2025_01_01_000001",
  "ts": "2025-01-01T00:00:00Z",
  "source": "ui|engine|cli|voice|sensor|server",
  "type": "command|signal|state|log|error",
  "name": "string_identifier",
  "payload": {},
  "context": {
    "session_id": "optional",
    "workspace_mode": "optional",
    "user_intent": "optional"
  },
  "severity": "debug|info|warn|error"
}
```

## Mapping to Current Modules (Examples)
- **UI command** → `source=ui`, `type=command`, `name=workspace.command`, `payload={"text": "coding mode"}`.
- **CLI command** → `source=cli`, `type=command`, `name=workspace.command`, `payload={"text": "save session"}`.
- **Sensor signal** → `source=sensor`, `type=signal`, `name=input.activity`, `payload={"kind": "mouse", "intensity": 0.7}`.
- **EI update** → `source=engine`, `type=state`, `name=ei.update`, `payload={"focus": 0.8, "stress": 0.2}`.
- **Voice output** → `source=voice`, `type=log`, `name=voice.speak`, `payload={"text": "Processing command"}`.

## Notes
- This model is intentionally minimal and descriptive.
- It does not introduce new behavior or requirements.
