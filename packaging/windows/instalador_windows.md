# Cómo crear el instalador de Windows de Ansul Flow Calculator

La app está escrita en Python/PySide6, así que el `.exe` de Windows **debe
compilarse en Windows** (no se puede generar de forma confiable desde Mac o
Linux). Este proyecto ya trae listos todos los archivos necesarios en
`packaging/windows/`; solo falta ejecutarlos. Hay dos caminos — elige el que
te acomode:

- **Opción A — tienes acceso a una PC con Windows** (la tuya, una prestada,
  o una máquina virtual de Windows): la más directa, todo se hace ahí.
- **Opción B — no tienes una PC con Windows** (por ejemplo, si solo usas
  Mac): usa GitHub Actions para compilar el instalador en una máquina de
  Windows en la nube, gratis, sin instalar nada. Requiere subir el
  proyecto a un repositorio de GitHub (puede ser privado).

Cualquiera de las dos produce el mismo resultado: un archivo
`AnsulFlowCalculator_Setup.exe` que el usuario final descarga, ejecuta, y
le instala la app con acceso directo en el Escritorio y en el menú Inicio
— como cualquier programa de Windows normal.

---

## Opción A: compilar en una PC con Windows

### 1. Requisitos (una sola vez)

1. **Python 3.12** (sirve de 3.10 a 3.13; la 3.12 es la que se probó) —
   descárgalo de [python.org/downloads](https://www.python.org/downloads/).
   En la primera pantalla del instalador marca la casilla **"Add
   python.exe to PATH"** antes de presionar "Install Now". Si ya tenías
   Python instalado sin esa casilla, vuelve a correr el instalador →
   "Modify" y actívala.
2. **Inno Setup 6.3 o más reciente** (gratis) — descárgalo de
   [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php) e instálalo
   con las opciones por defecto. Esto es lo que arma el instalador final
   a partir del programa ya compilado.

Para confirmar que Python quedó bien, abre el "Símbolo del sistema" (tecla
Windows → escribe `cmd` → Enter) y escribe `python --version`. Debe
responder algo como `Python 3.12.x`. Si en vez de eso se abre la Microsoft
Store, Python no quedó en el PATH: repite el paso 1.

### 2. Compilar el programa (PyInstaller)

1. Descomprime `AnsulFlowCalculator_Windows.zip` en una carpeta fija, por
   ejemplo `C:\Proyectos\AnsulFlowCalculator_Windows`. Revisa que dentro
   de esa carpeta estén directamente `main.py`, `ansul\` y `packaging\` —
   si al descomprimir quedó una carpeta dentro de otra con el mismo
   nombre, usa la de adentro.
2. Entra a `packaging\windows\` y haz **doble clic en
   `build_windows.bat`**. (También lo puedes correr desde el Símbolo del
   sistema; el script se ubica solo en la carpeta correcta.)
3. El script crea un entorno virtual, instala las dependencias (PySide6,
   reportlab, PyInstaller) y compila el programa. La primera vez tarda
   varios minutos porque descarga ~200 MB de librerías; las siguientes
   veces es más rápido. Al terminar debe decir **"Listo"** y el programa
   queda en:

   ```
   dist\AnsulFlowCalculator\AnsulFlowCalculator.exe
   ```

   Si en lugar de "Listo" aparece un mensaje de ERROR, la ventana se queda
   abierta: mándame una captura de las últimas líneas.
4. Pruébalo haciendo doble clic en ese `.exe` antes de seguir, para
   confirmar que la app abre bien. Ojo: ese `.exe` necesita la carpeta
   `_internal` que está junto a él — no lo copies suelto a otro lado; para
   repartirlo usa el instalador del paso 3.

### 3. Crear el instalador (Inno Setup)

1. Abre **Inno Setup Compiler**.
2. Abre el archivo `packaging\windows\installer.iss` (menú File → Open).
3. Presiona **Compile** (o F9).
4. El instalador queda en:

   ```
   packaging\windows\output\AnsulFlowCalculator_Setup.exe
   ```

Ese archivo es el que compartes o instalas. Al ejecutarlo, instala la app
(sin pedir permisos de administrador, con la opción de crear acceso
directo en el Escritorio) y queda lista para usarse — no necesita Python
instalado en la máquina donde se instala, PyInstaller ya empaquetó todo lo
necesario.

Opcional: en `installer.iss`, la línea `MyAppPublisher "Tu empresa"` es el
nombre que aparece como editor en "Agregar o quitar programas"; cámbiala si
quieres que diga otra cosa.

### Cada vez que actualices el programa

Reemplaza los archivos del código (`ansul\`, `main.py`) por la versión
nueva y repite los pasos 2 y 3 (no hace falta reinstalar Python ni Inno
Setup). Sube el número de la línea `MyAppVersion` en
`packaging\windows\installer.iss` antes de compilar (esta entrega ya viene
en `1.1.0`).

---

## Opción B: compilar en la nube con GitHub Actions (sin PC con Windows)

Ya se agregó el archivo `.github/workflows/build-windows.yml`, que le pide
a GitHub que arme el instalador en una máquina de Windows temporal. Pasos:

1. Sube este proyecto a un repositorio de GitHub (puede ser **privado** —
   no hace falta que sea público). Si nunca lo has hecho:
   [docs.github.com/es/get-started/quickstart](https://docs.github.com/es/get-started/quickstart/create-a-repo).
2. En GitHub, entra a la pestaña **Actions** del repositorio.
3. Elige el workflow **"Compilar instalador de Windows"** en la lista de
   la izquierda.
4. Presiona **Run workflow** (botón verde) → **Run workflow** de nuevo
   para confirmar.
5. Espera unos minutos a que termine (verás una marca verde ✓ cuando
   acabe).
6. Entra a esa ejecución terminada y baja hasta la sección **Artifacts**:
   ahí aparece **AnsulFlowCalculator_Setup** — descárgalo (es un .zip que
   trae adentro el `AnsulFlowCalculator_Setup.exe`).

Ese `.exe` es idéntico al que se generaría con la Opción A, solo que se
compiló en la nube. También puedes hacer que se genere automáticamente
cada vez que subas una etiqueta de versión (`git tag v1.0.0 && git push
--tags`), sin tener que entrar manualmente a "Run workflow".

---

## Cómo actualizar una instalación existente

**No hace falta desinstalar ni reinstalar desde cero.** El mismo
`AnsulFlowCalculator_Setup.exe` que instala el programa por primera vez
también sirve como paquete de actualización: `installer.iss` ya trae un
identificador fijo (`AppId`) que no cambia entre versiones, así que cuando
alguien ejecuta un instalador nuevo en una PC que ya tiene el programa,
Windows/Inno Setup lo reconoce como "la misma app" y simplemente reemplaza
los archivos del programa con la versión nueva — no crea una segunda copia
ni pide desinstalar la anterior primero.

Para publicar una actualización:

1. Haz los cambios al código como siempre.
2. (Opcional pero recomendado) sube en 1 el número de `MyAppVersion` en
   `packaging\windows\installer.iss` — así el usuario ve el número de
   versión correcto en "Agregar o quitar programas" de Windows. No es
   obligatorio: aunque lo dejes igual, la actualización de todas formas
   sobreescribe los archivos correctamente.
3. Vuelve a compilar (Opción A o B de arriba) para generar el nuevo
   `AnsulFlowCalculator_Setup.exe`.
4. Comparte ese archivo con los usuarios — lo ejecutan igual que la
   primera vez ("Siguiente, Siguiente, Instalar"), sin desinstalar nada a
   mano.

Lo único que **no** se toca en una actualización son los datos del
usuario (`Documentos\AnsulFlowCalculator\ansulcalc_db.json`), porque viven
fuera de la carpeta de instalación — sus proyectos, sistemas, riesgos y
catálogo propio quedan intactos.

Si el programa está abierto cuando se corre el instalador nuevo, Windows
pedirá cerrarlo primero (Inno Setup lo detecta automáticamente y te avisa
en pantalla) — solo hay que cerrar la app y darle click a "Reintentar".

> Esto es distinto de una "actualización automática dentro de la app"
> (donde el programa mismo revisa si hay una versión nueva y se actualiza
> solo, sin que el usuario tenga que descargar y correr nada). Eso es una
> función aparte, más compleja de construir (necesita un servidor donde
> publicar cada versión y código de auto-actualización dentro de la app);
> si en algún momento te interesa, dímelo y lo evaluamos.

---

## Notas

- Versiones probadas para esta entrega: PySide6 6.11, reportlab 5.0 y
  PyInstaller 6.22 (las que instala hoy `build_windows.bat`).
- El instalador **no requiere que el usuario final tenga Python
  instalado** — PyInstaller empaqueta un Python completo junto con la
  app.
- Los datos del usuario (proyectos, sistemas, riesgos, catálogo propio) se
  siguen guardando en `Documentos\AnsulFlowCalculator\ansulcalc_db.json`,
  fuera de la carpeta de instalación — así que desinstalar y reinstalar
  una versión nueva no borra la información capturada.
- Si en algún momento quieres un ícono propio para el `.exe` (en vez del
  ícono genérico de Python), consigue un archivo `.ico`, colócalo en
  `packaging/windows/app.ico` y descomenta la línea `icon=` dentro de
  `AnsulFlowCalculator.spec`.
- Antivirus/SmartScreen: como el instalador no está firmado digitalmente
  (firmar cuesta un certificado de terceros), es posible que Windows
  muestre una advertencia de "Editor desconocido" la primera vez que
  alguien lo ejecute — es normal para instaladores sin firmar y no
  significa que tenga virus; el usuario final debe elegir "Más
  información" → "Ejecutar de todas formas".
