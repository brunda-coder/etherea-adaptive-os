# -*- mode: python ; coding: utf-8 -*-

import importlib.util

import importlib.util
from PyInstaller.utils.hooks import collect_all

block_cipher = None

def _maybe(module: str) -> str | None:
    return module if importlib.util.find_spec(module) is not None else None


hiddenimports = [
    name
    for name in (
def _maybe(mod):
    return mod if importlib.util.find_spec(mod) is not None else None

hiddenimports = [
    m for m in (
        _maybe("speech_recognition"),
        _maybe("pyttsx3"),
        _maybe("pyaudio"),
        _maybe("pynput"),
    )
    if name is not None
]
    ) if m
]

qt_datas, qt_binaries, qt_hidden = collect_all("PySide6")
hiddenimports += qt_hidden

datas = [
    ("core/assets", "core/assets"),
    ("docs", "docs"),
]
binaries = []
datas += qt_datas
binaries += qt_binaries

a = Analysis(
    ["main.py"],
    pathex=[],
] + qt_datas

binaries = qt_binaries

a = Analysis(
    ["etherea_launcher.py"],   # desktop launcher entry
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="EthereaOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
    [],
    exclude_binaries=True,
    name="EthereaOS",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="EthereaOS",
)
