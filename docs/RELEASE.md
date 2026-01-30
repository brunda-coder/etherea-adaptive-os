# Release Process

Trigger a release by pushing a tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build:
- `EthereaOS_Windows.exe`
- `EthereaOS_Linux.AppImage`

and upload both to the GitHub Release for that tag.
# Release Process (Current)

This repo uses **Release-only** GitHub Actions. Workflows run only when a GitHub Release is **published**.

## How to ship a release
1) Go to GitHub → **Releases** → **Draft a new release**
2) Choose a tag (example: `v1.0.0`)
3) Publish the release

## What happens automatically
- **Release Tests (pytest)** runs first (fast fail if tests fail).
- **Release Build (Windows EXE)** builds and uploads the EXE artifact to the Release.

## Notes
- Workflows do **not** run on every push/PR (no CI spam).
- If you need a manual run: use **workflow_dispatch** from Actions tab.
