# WebOS + Desktop Merge Report

## Status
READY TO MERGE

## WebOS must-pass
- DONE: zero-binary enforcement for `etherea-webos/**`
- DONE: 3D avatar scene, idle animation, lip-sync from mic amplitude, mic permission path + meter
- DONE: stress/focus + aurora ring diagnostics
- DONE: tutorial overlay with persistent skip
- DONE: workspaces: drawing/pdf/coding with IndexedDB persistence
- DONE: agent actions: create_ppt, summarize_pdf, generate_notes with deterministic offline outputs
- DONE: connectors + notifications UI with explicit web sandbox limitations
- DONE: selfcheck command validates core paths

## Desktop must-pass
- DONE: compileall, feature audit, runtime selftest run in CI job
- DONE: no binary additions introduced

## Technical limitations
- Browser sandbox cannot provide native OS control and external app automation; connectors are currently explicit stubs.
- If SpeechRecognition API is unavailable, WebOS falls back to listening-state + mic level pipeline.
