# Release Process

Trigger a release by pushing a tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build:
- `Etherea-<VERSION>-Windows.exe`
- `Etherea-<VERSION>-Linux.AppImage`
- `SHA256SUMS.txt`

and upload them to the GitHub Release for that tag.

## Direct Download Links (for website buttons)
- Latest:
  `https://github.com/<OWNER>/<REPO>/releases/latest/download/<FILENAME>`
- Versioned:
  `https://github.com/<OWNER>/<REPO>/releases/download/<TAG>/<FILENAME>`

## Notes
- Use `docs/release_notes_template.md` for release notes.
