# Aurora Canvas

## AuroraCanvasState fields
- `current_mode`: effective mode after DND/error rules are applied (idle/focus/break/blocked/error).
- `focus`, `stress`, `energy`: EI values driving attention and visuals.
- `workspace_id`, `workspace_name`: current workspace identity from the workspace registry.
- `session_active`: whether a workspace session is active.
- `layout_density`: calm/normal/dense derived from mode rules.
- `attention_level`: low/med/high derived from EI values.
- `suggested_actions`: filtered action list from the action registry and mode rules.
- `theme_profile`: `{time_of_day, emotion_tag, reduce_motion}` for canvas styling.
- `nonessential_opacity`, `spacing`, `panel_visibility`, `overlay_text`, `warning_text`, `last_saved`: UI rule outputs.

## Mode rules
- **idle**: calm layout, minimal actions, high nonessential opacity.
- **focus**: dense layout, reduced distractions, filtered tool actions.
- **break**: relaxed layout, gentle cues, limited actions.
- **blocked/DND**: frozen layout, muted overlay with “Override active”, actions filtered to overrides.
- **error**: warning strip visible, low intensity.

## Pipeline wiring
- The Aurora canvas raises an intent on action click.
- The decision pipeline resolves the intent via the action registry, emits events on the shared event spine, updates workspace state, and then updates the Aurora state store.
- The decision pipeline resolves the intent via the action registry, emits events, updates workspace state, and then updates the Aurora state store.
- The Avatar/Ethera pipeline still handles natural-language input; Aurora actions feed through the same intent → action → state update flow.
