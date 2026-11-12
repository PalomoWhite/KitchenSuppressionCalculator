# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para compilar Kitchen Suppression Calculator en
# macOS y Linux (Windows usa packaging/windows/KitchenSuppressionCalculator.spec,
# que además alimenta al instalador de Inno Setup).
#
# Uso, parado en la raíz del repositorio (la carpeta que contiene main.py):
#
#   python -m PyInstaller --noconfirm packaging/multiplataforma/KitchenSuppressionCalculator.spec
#
# Resultado:
#   macOS -> dist/KitchenSuppressionCalculator.app   (aplicación de Mac)
#   Linux -> dist/KitchenSuppressionCalculator/      (carpeta con el ejecutable
#                                                     KitchenSuppressionCalculator)
#
# La versión se toma de packaging/windows/installer.iss (MyAppVersion), para
# que haya un solo lugar donde cambiarla.

import re
import sys
from pathlib import Path

block_cipher = None

# Dentro de un .spec no existe "__file__"; PyInstaller define SPECPATH.
REPO_ROOT = Path(SPECPATH).resolve().parent.parent
MAIN_SCRIPT = str(REPO_ROOT / 'main.py')
APP_NAME = 'KitchenSuppressionCalculator'

_iss = (REPO_ROOT / 'packaging' / 'windows' / 'installer.iss').read_text(encoding='utf-8')
_m = re.search(r'#define\s+MyAppVersion\s+"([^"]+)"', _iss)
APP_VERSION = _m.group(1) if _m else '0.0.0'

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=[(str(REPO_ROOT / 'ansul' / 'ui' / 'assets'), 'ansul/ui/assets')],   # logotipo
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX puede dañar las bibliotecas de Qt en Mac/Linux
    console=False,      # app de escritorio (GUI), sin terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=str(Path(SPECPATH) / 'app.icns'),   # logotipo de la app de Mac
        bundle_identifier='io.github.palomowhite.kitchensuppressioncalculator',
        version=APP_VERSION,
        info_plist={
            'CFBundleDisplayName': 'Kitchen Suppression Calculator',
            'CFBundleName': 'Kitchen Suppression Calculator',
            'CFBundleShortVersionString': APP_VERSION,
            'NSHighResolutionCapable': True,
            'NSHumanReadableCopyright': 'Copyright (C) 2026 Miguel Alejandro Gutiérrez Torres — GPL-3.0',
        },
    )
