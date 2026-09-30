# Cómo generar el instalador (.apk) de Ansul Flow Calculator para Android

La app está escrita en Python/Kivy, y el `.apk` de Android **debe
compilarse en Linux** (la herramienta que empaqueta Python para Android,
Buildozer, no funciona en Windows ni en Mac de forma confiable). Este
proyecto ya trae listos todos los archivos necesarios en `android/` y
`packaging/android/`; solo falta ejecutarlos. Hay dos caminos — elige el
que te acomode:

- **Opción A — tienes acceso a una PC/máquina virtual con Linux**: la más
  directa, todo se hace ahí. Si tu Linux es una máquina virtual dentro de
  Windows o Mac, funciona igual.
- **Opción B — no tienes una máquina Linux a la mano**: usa GitHub
  Actions para compilar el APK en una máquina de Ubuntu en la nube,
  gratis, sin instalar nada. Requiere subir el proyecto a un repositorio
  de GitHub (puede ser privado).

Cualquiera de las dos produce el mismo resultado: un archivo
`.apk` que se instala en cualquier teléfono/tablet Android como cualquier
otra app.

> **Nota importante:** el `.apk` que producen ambas opciones es una
> compilación **de depuración (debug)**, sin firma para Play Store —
> perfecta para instalar directamente en tus propios equipos o
> compartirla por WhatsApp/Drive/USB con tu equipo, pero **no** lista
> para subir a Google Play (eso requiere firmarla con una clave propia,
> un paso aparte — avísame si en algún momento quieres publicarla ahí).

---

## ¿Tu única máquina es Windows? Usa WSL (Linux dentro de Windows)

Buildozer no corre de forma confiable directamente en Windows, pero
**WSL (Windows Subsystem for Linux)** te da una Ubuntu real corriendo
dentro de tu propio Windows — gratis, integrada, sin máquina virtual
aparte. Con WSL activado, sigues la **Opción A** de abajo tal cual,
dentro de esa Ubuntu.

### Instalar WSL (una sola vez)

1. Abre **PowerShell como Administrador** (clic derecho → "Ejecutar como
   administrador") y ejecuta:

   ```powershell
   wsl --install
   ```

   Esto instala WSL2 y Ubuntu por defecto. Si te pide reiniciar la PC,
   reinicia.
2. Al terminar el reinicio, Ubuntu debería abrirse sola (o búscala como
   "Ubuntu" en el menú de inicio) y te pedirá crear un usuario y
   contraseña para esa Ubuntu — es independiente de tu cuenta de
   Windows, invéntate cualquiera y no la olvides.
3. Ya estás dentro de una terminal de Linux real. A partir de aquí,
   sigue los pasos de la **Opción A** de esta guía (instalar
   dependencias, copiar el proyecto, compilar) exactamente igual que si
   fuera una PC con Linux — porque, para estos efectos, lo es.

   Un detalle práctico: para copiar el proyecto a esa Ubuntu, lo más
   simple es que dentro de la terminal de Ubuntu hagas:

   ```bash
   cd ~
   cp -r /mnt/c/Users/TU_USUARIO/Documents/AnsulFlowCalculator_Python .
   cd AnsulFlowCalculator_Python
   ```

   (ajusta la ruta a donde tengas el proyecto en Windows — WSL ve tus
   discos de Windows bajo `/mnt/c/`, `/mnt/d/`, etc.). Trabajar sobre la
   copia dentro de Ubuntu (`~/AnsulFlowCalculator_Python`) en vez de
   directo sobre `/mnt/c/...` hace que Buildozer compile notablemente
   más rápido.
4. Cuando termine de compilar, el `.apk` queda dentro de esa Ubuntu, en
   `~/AnsulFlowCalculator_Python/android/bin/`. Para copiarlo de vuelta a
   Windows y poder pasarlo a un teléfono:

   ```bash
   cp android/bin/*.apk /mnt/c/Users/TU_USUARIO/Desktop/
   ```

---

## Opción A: compilar en una máquina Linux (o en WSL, ver arriba)

### 1. Requisitos (una sola vez)

1. **Python 3.9 o superior**, `pip` y `git`.
2. **Buildozer** y sus dependencias del sistema (Buildozer a su vez baja
   automáticamente el Android SDK/NDK la primera vez que compilas — no
   hace falta instalarlos a mano):

   ```bash
   sudo apt update
   sudo apt install -y python3-pip build-essential git python3 python3-dev \
       ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
       zlib1g-dev openjdk-17-jdk unzip
   pip install --user buildozer cython
   ```

### 2. Compilar el APK

1. Copia todo el proyecto (la carpeta que contiene `main.py`, `ansul/` y
   `android/`) a la máquina Linux.
2. Desde la raíz del proyecto, ejecuta:

   ```bash
   bash packaging/android/build_android.sh
   ```

   Este script primero sincroniza una copia de `ansul/` dentro de
   `android/ansul/` (Buildozer solo empaqueta lo que está dentro de la
   carpeta `android/`, así que el motor de cálculo se copia ahí antes de
   compilar — nunca edites `android/ansul/` directamente, siempre
   sobrescribe con la versión real de `ansul/`), y luego llama a
   Buildozer. **La primera vez puede tardar 20-40 minutos** porque
   descarga el Android SDK/NDK; las siguientes compilaciones son mucho
   más rápidas.
3. Al terminar, el instalador queda en:

   ```
   android/bin/AnsulFlowCalculator-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
   ```

   (el nombre exacto incluye la versión y arquitecturas compiladas).

### 3. Instalar el APK en un teléfono

- Copia el `.apk` al teléfono (por USB, Drive, WhatsApp, etc.) y ábrelo
  desde el explorador de archivos del teléfono, o
- Con el teléfono conectado por USB y la depuración USB activada:
  ```bash
  adb install android/bin/*.apk
  ```

Android mostrará una advertencia de "instalar apps de fuentes
desconocidas" la primera vez — es normal para un `.apk` que no viene de
Play Store; hay que aceptarla para continuar.

### Cada vez que actualices el programa

Repite el paso 2 (`bash packaging/android/build_android.sh`). Si quieres
que el número de versión mostrado cambie, edita `version` en
`android/buildozer.spec` antes de compilar.

---

## Opción B: compilar en la nube con GitHub Actions (sin máquina Linux)

Ya se agregó el archivo `.github/workflows/build-android.yml`, que le
pide a GitHub que arme el APK en una máquina de Ubuntu temporal. Pasos:

1. Sube este proyecto a un repositorio de GitHub (puede ser **privado**
   — no hace falta que sea público). Si nunca lo has hecho:
   [docs.github.com/es/get-started/quickstart](https://docs.github.com/es/get-started/quickstart/create-a-repo).
2. En GitHub, entra a la pestaña **Actions** del repositorio.
3. Elige el workflow **"Compilar APK de Android"** en la lista de la
   izquierda.
4. Presiona **Run workflow** (botón verde) → **Run workflow** de nuevo
   para confirmar.
5. Espera a que termine — la primera vez puede tardar 30-45 minutos
   porque compila el Android SDK/NDK desde cero (verás una marca verde ✓
   cuando acabe).
6. Entra a esa ejecución terminada y baja hasta la sección **Artifacts**:
   ahí aparece **AnsulFlowCalculator-apk** — descárgalo (es un .zip que
   trae adentro el `.apk`).

También puedes hacer que se genere automáticamente cada vez que subas
una etiqueta de versión (`git tag v1.0.0 && git push --tags`), sin tener
que entrar manualmente a "Run workflow".

---

## Cómo actualizar una instalación existente

A diferencia de Windows (donde el mismo instalador sirve para actualizar
sin desinstalar), en Android **cada nuevo `.apk` que instales sobre uno
anterior actualiza la app automáticamente** siempre que:

- El `package.name` y `package.domain` en `android/buildozer.spec` no
  cambien (ya vienen fijos: `ansulflowcalculator` /
  `org.ansulflowcalculator`) — Android usa esa combinación para
  reconocer que es "la misma app".
- El nuevo APK esté firmado de la misma forma que el anterior (los APK
  de depuración que generan las Opciones A y B usan siempre la misma
  clave de depuración automática, así que esto no requiere ningún paso
  adicional mientras sigas usando este mismo flujo de compilación).

Entonces, para publicar una actualización: haz los cambios al código,
vuelve a compilar (Opción A o B) y comparte el nuevo `.apk` — el usuario
lo instala igual que la primera vez, sin desinstalar nada a mano, y sus
datos (proyectos, sistemas, riesgos) se conservan porque viven en el
almacenamiento privado de la app, no en el propio `.apk`.

---

## Notas

- **Datos del usuario**: se guardan en el almacenamiento privado de la
  app (accesible solo por Ansul Flow Calculator) — se conservan entre
  actualizaciones y se borran solo si el usuario desinstala la app o
  borra sus datos manualmente desde Ajustes de Android.
- **Reportes PDF**: se generan dentro del almacenamiento privado de la
  app y, si el teléfono lo permite, se ofrecen para compartir con el
  selector nativo de Android (WhatsApp, Drive, correo, etc.) mediante la
  librería `plyer`. Si compartir directamente no funciona en algún
  equipo (varía según fabricante/versión de Android), el PDF de todas
  formas queda guardado y la app avisa dónde — conviene probar esta
  parte en un teléfono real antes de repartir la app a tu equipo, y
  ajustar permisos en `android/buildozer.spec` si hiciera falta.
- **Ícono propio**: coloca un PNG en `android/data/icon.png` y
  descomenta la línea `icon.filename` en `android/buildozer.spec` para
  reemplazar el ícono genérico de Kivy.
- **Publicar en Google Play**: este flujo genera un APK de depuración,
  suficiente para instalar directamente o repartir por fuera de Play
  Store. Publicar en Play Store requiere generar un *Android App Bundle*
  firmado con una clave propia (un paso adicional, con su propio
  proceso de alta como desarrollador en Play Console) — es un tema
  aparte si llegas a necesitarlo.
- **Funciones aún no portadas a esta versión**: el buscador de catálogo
  de 65 modelos por marca y el diagrama en vivo del área protegida
  siguen siendo exclusivos de la versión de escritorio por ahora; el
  resto del flujo (proyectos, sistemas, las 17 categorías de riesgo con
  su cálculo completo, resumen de tanques/flow number, reportes PDF)
  está disponible igual que en escritorio.
