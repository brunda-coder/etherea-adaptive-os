#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-core.txt -r requirements-desktop.txt -r requirements-ui.txt
python -m pip install pyinstaller

if [[ -z "$VERSION" ]]; then
  VERSION="$(python -c 'from corund.version import __version__; print(__version__)')"
fi
if [[ "$VERSION" == v* ]]; then
  VERSION="${VERSION#v}"
fi

rm -rf build dist
rm -f Etherea-*.AppImage

pyinstaller --clean --noconfirm --onefile etherea.spec

APPDIR="dist/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "dist/Etherea" "$APPDIR/usr/bin/Etherea"
cp "scripts/appimage/Etherea.desktop" "$APPDIR/usr/share/applications/Etherea.desktop"
cp "corund/assets/avatar.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/Etherea.png"

cat > "$APPDIR/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/Etherea" "$@"
EOF
chmod +x "$APPDIR/AppRun"

LINUXDEPLOYQT="linuxdeployqt.AppImage"
if [[ ! -f "$LINUXDEPLOYQT" ]]; then
  curl -L -o "$LINUXDEPLOYQT" https://github.com/probonopd/linuxdeployqt/releases/download/continuous/linuxdeployqt-continuous-x86_64.AppImage
  chmod +x "$LINUXDEPLOYQT"
fi

export APPIMAGE_EXTRACT_AND_RUN=1
./"$LINUXDEPLOYQT" "$APPDIR/usr/share/applications/Etherea.desktop" \
  -appimage \
  -bundle-non-qt-libs \
  -unsupported-allow-new-glibc

APPIMAGE_NAME="Etherea-${VERSION}-Linux.AppImage"

mv Etherea-*.AppImage "$APPIMAGE_NAME"
chmod +x "$APPIMAGE_NAME"

export ETHEREA_DATA_DIR="$ROOT_DIR/selftest"
QT_QPA_PLATFORM=offscreen "./$APPIMAGE_NAME" --self-test
