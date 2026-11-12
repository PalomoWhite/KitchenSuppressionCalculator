; Script de Inno Setup para crear el instalador de Windows de
; Kitchen Suppression Calculator, a partir de la carpeta que genera PyInstaller
; (dist\KitchenSuppressionCalculator\).
;
; Uso:
;   1. Compila primero con build_windows.bat (debe existir
;      dist\KitchenSuppressionCalculator\KitchenSuppressionCalculator.exe).
;   2. Abre este archivo con Inno Setup (Compiler) y presiona "Compile"
;      (o desde línea de comandos: ISCC.exe packaging\windows\installer.iss).
;   3. El instalador queda en packaging\windows\output\
;      KitchenSuppressionCalculator_Setup.exe
;
; Cambia MyAppVersion cuando publiques una nueva versión.

#define MyAppName "Kitchen Suppression Calculator"
#define MyAppVersion "1.3.2"
#define MyAppPublisher "Miguel Alejandro Gutiérrez Torres"
#define MyAppExeName "KitchenSuppressionCalculator.exe"
; Ruta a la carpeta que generó PyInstaller (relativa a este .iss)
#define MyDistDir "..\..\dist\KitchenSuppressionCalculator"

[Setup]
AppId={{C332CC2F-E7ED-40D6-8CDD-6C8791B439F6}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Usar siempre el nombre actual del programa para la carpeta del menú Inicio
; (sin esto, al actualizar se reutilizaba la de "Ansul Flow Calculator").
UsePreviousGroup=no
OutputDir=output
OutputBaseFilename=KitchenSuppressionCalculator_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; Instalar solo para el usuario actual evita pedir permisos de administrador;
; cambia a "admin" si prefieres instalar para todos los usuarios del equipo.
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"

[InstallDelete]
; Limpieza al actualizar desde versiones anteriores a la 1.3.0, cuando el
; programa se llamaba "Ansul Flow Calculator": se borran el .exe viejo y sus
; accesos directos, que seguían en el Escritorio sin el logotipo nuevo.
Type: files; Name: "{app}\AnsulFlowCalculator.exe"
Type: files; Name: "{autodesktop}\Ansul Flow Calculator.lnk"
Type: filesandordirs; Name: "{autoprograms}\Ansul Flow Calculator"
; Dependencias de la versión anterior: se reemplazan completas para no dejar
; bibliotecas viejas mezcladas con las nuevas.
Type: filesandordirs; Name: "{app}\_internal"

[Files]
; Copia TODO el contenido de la carpeta generada por PyInstaller (el .exe
; más sus dependencias .dll/.pyd).
Source: "{#MyDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
