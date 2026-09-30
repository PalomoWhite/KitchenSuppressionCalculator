#!/usr/bin/env bash
# Compila el .apk de Ansul Flow Calculator para Android.
# Uso: ejecutar desde cualquier carpeta, con bash:
#   bash packaging/android/build_android.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> Sincronizando ansul/ dentro de android/ansul (copia de compilación)…"
rm -rf android/ansul
cp -r ansul android/ansul

echo "==> Compilando APK con buildozer (la primera vez descarga el Android"
echo "    SDK/NDK — puede tardar 20-40 minutos; las siguientes veces es más rápido)…"
cd android
buildozer -v android debug

echo
if ls bin/*.apk >/dev/null 2>&1; then
    echo "Listo. El APK quedó en:"
    ls -la bin/*.apk
else
    echo "No se encontró ningún .apk — revisa el log de buildozer arriba para ver el error."
    exit 1
fi
