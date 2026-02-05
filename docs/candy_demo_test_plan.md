# Candy Demo Test Plan

## Manual Smoke
1. Run `python main.py`.
2. Open Settings → Appearance and toggle Candy theme.
3. Verify glossy cards, rounded command palette, and candy gradients.
4. Open Settings → Avatar and toggle Free Roam + Freeze.
5. Confirm avatar bounces within bounds and sparkles on click.
6. Open Settings → Emotion and toggle Enable + Camera Opt-In (observe local-only label).
7. Trigger idle time and confirm a neutral check-in message when confidence is low.
8. Open Settings → Voice and enable Dramatic Mode; watch bubble text update.

## Automated Checks
- `pytest tests/test_theme_toggle.py tests/test_avatar_bounds.py tests/test_emotion_confidence.py`
