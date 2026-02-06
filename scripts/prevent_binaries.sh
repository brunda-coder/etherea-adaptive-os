#!/usr/bin/env bash
set -euo pipefail

MAX_BYTES=$((5 * 1024 * 1024))
blocked_exts=(png jpg jpeg webp gif wav mp3 mp4 bin gltf glb exe appimage msi dmg zip 7z pdf ttf otf)
allow_asset_roots=(assets/ core/assets/ corund/assets/)

mode="staged"
range=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --range)
      mode="range"
      range="${2:-}"
      shift 2
      ;;
    *)
      echo "[prevent_binaries] unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$mode" == "range" ]]; then
  if [[ -z "$range" ]]; then
    echo "[prevent_binaries] --range requires a git range (example: base...HEAD)" >&2
    exit 2
  fi
  staged=$(git diff --name-only --diff-filter=A "$range")
else
  staged=$(git diff --cached --name-only --diff-filter=A)
fi

[ -z "$staged" ] && exit 0

is_allowlisted_asset_path() {
  local path="$1"
  for root in "${allow_asset_roots[@]}"; do
    if [[ "$path" == "$root"* ]]; then
      return 0
    fi
  done
  return 1
}

is_blocked_ext() {
  local ext="$1"
  for blocked in "${blocked_exts[@]}"; do
    if [[ "$ext" == "$blocked" ]]; then
      return 0
    fi
  done
  return 1
}

err=0
while IFS= read -r file; do
  [ -z "$file" ] && continue

  ext=""
  if [[ "$file" == *.* ]]; then
    ext="${file##*.}"
    ext="${ext,,}"
  fi

  if [[ -n "$ext" ]] && is_blocked_ext "$ext"; then
    if ! is_allowlisted_asset_path "$file"; then
      echo "[prevent_binaries] blocked extension for new file outside allowlist: $file"
      err=1
    fi
  fi

  if [[ -f "$file" ]]; then
    size=$(wc -c < "$file")
    if (( size > MAX_BYTES )); then
      echo "[prevent_binaries] file too large (>5MB): $file (${size} bytes)"
      err=1
    fi
  fi
done <<< "$staged"

if (( err != 0 )); then
  echo "[prevent_binaries] commit blocked. Keep binary assets out of git (except curated assets under allowlisted folders)."
  exit 1
fi
