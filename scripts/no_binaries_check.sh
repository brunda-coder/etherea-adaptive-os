#!/usr/bin/env bash
set -euo pipefail

forbidden_ext='\.(png|jpg|jpeg|webp|gif|wav|mp3|mp4|exe|msi|apk|aab|zip|7z|pdf|ttf|otf)$'

# Existing curated desktop binaries outside etherea-webos are allowlisted.
readonly ALLOWLIST_OUTSIDE_WEBOS=(
  "assets/audio/ui_click.wav"
  "assets/audio/ui_success.wav"
  "assets/audio/ui_whoosh.wav"
  "assets/avatar/face_idle.webp"
  "assets/avatar_hero/avatar_full_body.png"
  "core/assets/audio/etherea_theme_a.wav"
  "corund/assets/audio/etherea_theme_a.wav"
  "corund/assets/audio/etherea_theme_b.wav"
  "corund/assets/audio/etherea_theme_c.wav"
  "corund/assets/avatar.png"
  "corund/assets/avatar_hero/base.png"
  "corund/assets/avatar_hero/indian_mentor.png"
  "exports/export_20260114_1424.zip"
)

declare -A allow_map=()
for path in "${ALLOWLIST_OUTSIDE_WEBOS[@]}"; do
  allow_map["$path"]=1
done

violations=()
while IFS= read -r path; do
  [[ -z "$path" ]] && continue

  if [[ "$path" == etherea-webos/* ]]; then
    violations+=("$path")
    continue
  fi

  if [[ -z "${allow_map[$path]+x}" ]]; then
    violations+=("$path")
  fi
done < <(git ls-files | grep -Ei "$forbidden_ext" || true)

if (( ${#violations[@]} > 0 )); then
  echo "❌ Binary policy violations detected:"
  printf ' - %s\n' "${violations[@]}"
  exit 1
fi

echo "✅ Binary policy check passed (etherea-webos/** contains zero binaries)."
