[app]

title = Ansul Flow Calculator
package.name = ansulflowcalculator
package.domain = org.ansulflowcalculator

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
# "ansul" se sincroniza aquí como copia de compilación justo antes de
# invocar buildozer (ver packaging/android/build_android.sh) — nunca se
# edita directamente, siempre es un espejo de la carpeta real en la raíz
# del proyecto.
source.exclude_dirs = tests, bin, .buildozer, __pycache__

version = 1.0.0
requirements = python3,kivy==2.3.1,kivymd==2.0.0,reportlab,plyer,pillow

orientation = portrait
fullscreen = 0

# Ícono / splash propios (opcional): coloca los archivos y descomenta.
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
