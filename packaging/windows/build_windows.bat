@echo off
REM Compila Kitchen Suppression Calculator para Windows con PyInstaller.
REM
REM Se puede ejecutar de dos formas:
REM   - Doble clic sobre este archivo (packaging\windows\build_windows.bat), o
REM   - Desde el Simbolo del sistema:  packaging\windows\build_windows.bat
REM En ambos casos el script se cambia solo a la carpeta raiz del proyecto
REM (la que contiene main.py), asi que no importa desde donde se abra.
REM
REM Requiere Python 3.10 a 3.13 instalado y en el PATH (python.org, marcando
REM la casilla "Add python.exe to PATH" durante la instalacion).

setlocal

REM --- Ir a la raiz del proyecto (dos carpetas arriba de este .bat) ---
cd /d "%~dp0..\.."
if not exist main.py (
    echo *** ERROR: no se encontro main.py en "%CD%". ***
    echo *** Este archivo debe estar dentro de packaging\windows\ del proyecto. ***
    pause
    exit /b 1
)
echo Carpeta del proyecto: %CD%
echo.

REM --- Verificar que Python este instalado y en el PATH ---
python --version >nul 2>&1
if errorlevel 1 (
    echo *** ERROR: no se encontro Python. ***
    echo Instala Python 3.12 desde https://www.python.org/downloads/ y marca
    echo la casilla "Add python.exe to PATH" durante la instalacion.
    echo Despues cierra y vuelve a abrir esta ventana.
    pause
    exit /b 1
)
python --version

echo === 1/4: Creando entorno virtual (venv) si no existe ===
if not exist venv\Scripts\python.exe (
    python -m venv venv
    if errorlevel 1 (
        echo *** ERROR: no se pudo crear el entorno virtual. ***
        pause
        exit /b 1
    )
)

echo === 2/4: Instalando dependencias ===
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo *** ERROR: fallo la instalacion de dependencias. Revisa tu conexion ***
    echo *** a internet y el mensaje de error de arriba.                    ***
    pause
    exit /b 1
)

echo === 3/4: Limpiando compilaciones anteriores ===
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo === 4/4: Compilando con PyInstaller ===
python -m PyInstaller --noconfirm packaging\windows\KitchenSuppressionCalculator.spec

REM Verificar que el .exe realmente se haya creado antes de decir "Listo".
if not exist dist\KitchenSuppressionCalculator\KitchenSuppressionCalculator.exe (
    echo.
    echo *** ERROR: PyInstaller no genero el .exe. Revisa el mensaje de error ***
    echo *** de arriba ^(la ultima linea suele decir "Error" o "Traceback"^).  ***
    endlocal
    pause
    exit /b 1
)

echo.
echo Listo. El programa quedo en:
echo     %CD%\dist\KitchenSuppressionCalculator\KitchenSuppressionCalculator.exe
echo Pruebalo con doble clic antes de crear el instalador (paso 3 de
echo packaging\windows\instalador_windows.md).

endlocal
pause
