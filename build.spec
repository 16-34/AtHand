# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置"""

import sys
import os
from PySide6.QtCore import QLibraryInfo

block_cipher = None

src_path = os.path.join(SPECPATH, "src")

a = Analysis(
    [os.path.join(SPECPATH, "run.py")],
    pathex=[src_path],
    binaries=[],
    datas=[
        (os.path.join(src_path, "resources"), "resources"),
    ],
    hiddenimports=[
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "pynput.keyboard._darwin",
        "pynput.keyboard._win32",
        "pynput.keyboard._xorg",
        "pynput.mouse._darwin",
        "pynput.mouse._win32",
        "pynput.mouse._xorg",
        "openai",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyqtbinary = []

# PySide6 插件
pyside6_dir = os.path.dirname(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath))
for root, dirs, files in os.walk(pyside6_dir):
    for f in files:
        if f.endswith((".dll", ".so", ".dylib")):
            src_file = os.path.join(root, f)
            rel_path = os.path.relpath(src_file, pyside6_dir)
            pyqtbinary.append((os.path.join("PySide6", rel_path), src_file, "BINARY"))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries + pyqtbinary,
    a.zipfiles,
    a.datas,
    [],
    name="AtHand",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(src_path, "resources", "icon.png"),
)

# macOS: 创建 .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="AtHand.app",
        icon=os.path.join(src_path, "resources", "icon.png"),
        bundle_identifier="com.athand.app",
    )
