# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import importlib.util

from PyInstaller.utils.hooks import collect_all

block_cipher = None


def _maybe(module: str) -> str | None:
    return module if importlib.util.find_spec(module) is not None else None


hiddenimports = [
    mod
    for mod in (
        _maybe("speech_recognition"),
        _maybe("pyttsx3"),
        _maybe("pyaudio"),
        _maybe("pynput"),
        _maybe("numpy"),
        _maybe("pygame"),
    )
    if mod
]

qt_datas, qt_binaries, qt_hidden = collect_all("PySide6")
hiddenimports += qt_hidden

datas = [
    ("assets", "assets"),
    ("core/assets", "core/assets"),
    ("corund/assets", "corund/assets"),
    ("docs", "docs"),
]
datas += qt_datas
binaries = qt_binaries

a = Analysis(
    ["etherea_launcher.py"],
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
    name="Etherea",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
