# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para Kitchen Suppression Calculator (Windows).
#
# Uso (desde Windows, con el venv del proyecto activado, parado en la raíz
# del repositorio — la carpeta que contiene main.py):
#
#   pyinstaller packaging\windows\KitchenSuppressionCalculator.spec
#
# El resultado queda en dist\KitchenSuppressionCalculator\KitchenSuppressionCalculator.exe
# (modo "onedir": una carpeta con el .exe y sus dependencias — arranca más
# rápido que el modo "onefile" y es lo que espera installer.iss).
#
# Si agregas un ícono .ico propio, colócalo en packaging/windows/app.ico y
# descomenta la línea "icon=" más abajo.

import sys
from pathlib import Path

block_cipher = None

# Raíz del repo = dos niveles arriba de este archivo (packaging/windows/..).
# OJO: dentro de un .spec de PyInstaller NO existe la variable "__file__"
# (el archivo se ejecuta con exec(), no como un módulo importado) — hay que
# usar "SPECPATH", que PyInstaller sí define automáticamente como la carpeta
# que contiene este .spec.
REPO_ROOT = Path(SPECPATH).resolve().parent.parent
MAIN_SCRIPT = str(REPO_ROOT / 'main.py')

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KitchenSuppressionCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # sin consola: es una app de escritorio (GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=str(Path(SPECPATH) / 'app.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KitchenSuppressionCalculator',
)
