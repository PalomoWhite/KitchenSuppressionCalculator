# Ansul Flow Calculator (versión de escritorio en Python)

Calculadora de apoyo para el diseño preliminar de sistemas de supresión
**ANSUL(R) R-102** para cocinas comerciales. Es el equivalente en Python /
PySide6 de la herramienta web `AnsulCalc.html`, con la misma lógica de
cálculo (verificada línea por línea contra el original) y las mismas
funciones: proyectos, sistemas (antes "cocinas"), riesgos (antes "equipos"),
catálogo de 65 modelos por marca, selección de tanques/cartuchos, y
reportes PDF.

> **AVISO IMPORTANTE:** esta aplicación es una **ayuda de diseño preliminar**
> basada en el manual ANSUL(R) R-102 (Part No. 418087) y la Hoja Resumen
> F-2015158-01_LAS. El diseño final de cualquier sistema R-102 debe ser
> verificado y sellado por un diseñador certificado ANSUL R-102, conforme a
> NFPA 17A y los códigos locales aplicables.

## Instalación

Requiere Python 3.9 o superior.

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

## Qué hace

- **Proyectos → Sistemas → Riesgos**: organiza el trabajo igual que la
  herramienta web (un restaurante puede tener varios sistemas/campanas,
  cada uno con sus propios riesgos/equipos protegidos). "Sistema" es el
  nuevo nombre de lo que antes se llamaba "Cocina", y "Riesgo" el nuevo
  nombre de lo que antes se llamaba "Equipo" — son la misma entidad, solo
  cambió la etiqueta que ve el usuario.
- **17 categorías de riesgo**: freidoras, sartén de volteo, estufa (1, 2, 4 o
  6 quemadores), plancha, parrilla/asador (gas, eléctrico, carbón, leña),
  **robata** (boquillas 1N/3N para combustible sólido — carbón o leña),
  asador de cadena, asador vertical, salamandra, wok, horno combi, **marmita**,
  ducto, pleno (en metros) y precipitador electrostático — cada una con su
  propio formulario, su **diagrama en vivo del área protegida** (se dibuja a
  medida que se capturan las medidas) y su propia lógica de cálculo tomada
  del manual R-102 (Sección 4).
- **Horno Combi y Marmita (no requieren protección)**: el manual R-102 no
  incluye una boquilla estándar para ninguno de los dos — el horno combi
  por tener protección tipo UL 300 dentro del gabinete cerrado, y la
  marmita por cocinar con agua/vapor (no con aceite), así que no genera
  vapores grasosos. Ambos se registran en el sistema solo como referencia
  (sin boquillas ni flow number) para no perder el conteo de equipos de la
  cocina, no porque el programa no sepa calcularlos.
- **Modularización automática de riesgos sobredimensionados**: en Freidora,
  Sartén de Volteo, Estufa, Plancha, Parrilla/Robata, si el riesgo es más
  grande de lo que cubre una sola boquilla, el programa calcula
  automáticamente cuántas zonas (módulos) se necesitan y con qué boquilla,
  dividiendo el riesgo por su lado más largo — el mismo método que usa el
  manual R-102 para freidoras y sartenes de volteo (Sección 4, pág. 4-10 a
  4-12). El campo "Número de módulos" puede dejarse en 1 (cálculo
  automático) o aumentarse si se quieren forzar más zonas de las mínimas
  necesarias.
- **Estufa**: el número de quemadores (1/2/4/6) y el combustible son solo
  informativos — el manual R-102 no distingue boquillas por quemadores,
  sino por las medidas del área de cocción, así que no cambian el cálculo.
  Una estufa de 6 quemadores sobredimensionada se modulariza igual que
  cualquier otra, mostrando todas las opciones de proximidad (alta, media o
  baja) que apliquen, no una sola fija.
- **Catálogo de modelos por marca**: 65 fichas ya cargadas (Frymaster, Pitco,
  Henny Penny, Garland, Taylor, Nieco, DUKE, Belshaw, etc.) más un catálogo
  propio editable (menú **Catálogo → Administrar mi catálogo**).
- **Duplicar riesgo**: copia un riesgo/equipo ya capturado (con sus medidas
  y resultado) para agilizar sistemas con varias piezas iguales o muy
  similares.
- **Duplicar sistema**: copia un sistema completo (nombre, todos sus
  riesgos y el override manual de tanques si lo tenía) dentro del mismo
  proyecto, para agilizar proyectos con varios sistemas muy parecidos.
- **Selección de tanques y cartuchos**: automática según el "flow number"
  total del sistema (1.5 gal, 3 gal, sistemas múltiples), o **manual**
  (elige a mano cuántos tanques de cada tamaño instalar) desde la propia
  vista del sistema — si el galonaje manual resulta insuficiente para el
  flow number calculado, la app lo advierte.
- **Medidas "Largo x Ancho" en la tabla de riesgos**: la tabla de "Riesgos,
  ductos y plenos" de cada sistema muestra una columna con las medidas ya
  capturadas de cada riesgo (freidora, sartén de volteo, estufa, plancha,
  parrilla/asadores/robata: Largo x Ancho; wok y ducto redondo: Ø diámetro;
  ducto rectangular: Ancho x Alto; pleno: Largo x Ancho en metros), para
  verlas de un vistazo sin tener que abrir cada riesgo. Las etiquetas de
  captura de cada formulario también se unificaron a "Largo (in)" / "Ancho
  (in)" en las categorías con footprint rectangular (antes algunas decían
  "Fondo", "Longitud interna", etc.) — el ducto rectangular conserva "Ancho"
  / "Alto" porque describe una sección transversal, no un footprint.
- **Columna "Profundidad" (por separado de "Largo x Ancho")**: Wok,
  Parrilla, Asador de Carbón, Asador de Leña y Robata además capturan una
  medida de profundidad (la del wok, o la de la cama de brasas/carbón/leña)
  que no forma parte del área — ahora aparece en su propia columna en la
  tabla de riesgos, en vez de quedar fuera de la vista. El resto de
  categorías, que no tienen esta medida, muestran "—".
- **Convertidor de unidades** (menú **Herramientas**): pies ↔ metros, de uso
  general para apoyar la captura de medidas. Además, el formulario de
  "Agregar riesgo" trae su propio convertidor rápido integrado (metros ↔
  pies y pulgadas ↔ centímetros), justo arriba de las medidas de cada
  categoría, para convertir sin salir del formulario ni abrir el menú
  Herramientas.
- **Consecutivo de cotización**: campo a nivel proyecto que se incluye en el
  encabezado de los reportes PDF.
- **Reportes PDF** por sistema o por proyecto completo, con desglose de
  riesgos, resumen de materiales, **capacidad total de flujo (flow
  number)** del sistema y del proyecto completo, y lista de boquillas
  requeridas. El botón de generar PDF permanece deshabilitado hasta que el
  proyecto/sistema tenga riesgos asignados, y el botón de agregar sistema
  hasta que exista al menos un proyecto.
- **Respaldo / restauración** de todos los datos en un archivo `.json`
  (menú **Archivo**).
- **Referencia rápida** (menú **Referencia**): tabla de boquillas y
  requisitos de tubería de distribución por tamaño de sistema, tomados de la
  Hoja Resumen.
- **Interfaz con la misma paleta de la herramienta web** (azul ANSUL
  `#0554a3`, tarjetas con bordes redondeados) mediante una hoja de estilos
  Qt (QSS) que reproduce las variables de `AnsulCalc.html`.

Los datos se guardan automáticamente en:

- Windows/Mac/Linux: `~/Documents/AnsulFlowCalculator/ansulcalc_db.json`
  (o `~/Documentos/...` si el sistema está en español).

## Instalador de Windows

Para distribuir la app a usuarios de Windows sin que necesiten instalar
Python, ver la guía paso a paso en
[`packaging/windows/instalador_windows.md`](packaging/windows/instalador_windows.md)
(incluye una opción para compilarlo en la nube con GitHub Actions si no
tienes una PC con Windows a la mano).

## Versión Android

Existe una versión para Android en `android/`, escrita con Kivy/KivyMD.
Reutiliza sin cambios el motor de cálculo y la persistencia de la
versión de escritorio (`ansul/engine.py`, `category_defs.py`, `data.py`,
`store.py`, `report.py`) — solo la interfaz está reconstruida con
widgets de Kivy, incluyendo un **formulario dinámico genérico**
(`android/ui/dynamic_form.py`) que lee las mismas especificaciones
declarativas de `category_defs.py` que usa la versión de escritorio, así
que cubre las 17 categorías de riesgo automáticamente, sin una pantalla
distinta por categoría. Cubre proyectos, sistemas, riesgos (con el
cálculo completo de las 17 categorías, incluida la selección de
boquilla cuando hay varias opciones), resumen de tanques/flow number por
sistema, y generación + compartir de reportes PDF. El buscador de
catálogo de 65 modelos y el diagrama en vivo del área protegida, por
ahora, siguen siendo exclusivos de la versión de escritorio.

Para compilar el `.apk`, ver la guía paso a paso en
[`packaging/android/instalador_android.md`](packaging/android/instalador_android.md)
(incluye una opción para compilarlo en la nube con GitHub Actions si no
tienes una máquina Linux a la mano — Buildozer, la herramienta que
empaqueta Python para Android, solo compila en Linux). Para probar la
app en escritorio antes de compilarla:

```bash
pip install -r android/requirements.txt
python android/main.py
```

## Estructura del proyecto

```
main.py                     Punto de entrada
ansul/
  data.py                   Tablas de referencia (boquillas, grupos de
                             freidoras, opciones de parrilla, tanques, etc.)
  model_catalog.py           Catálogo de 65 modelos específicos por marca
  engine.py                  Motor de cálculo (puerto 1:1 de AnsulCalc.html)
  category_defs.py           Definición de campos de captura por categoría
  store.py                   Persistencia local en JSON (proyectos/sistemas/riesgos)
  report.py                  Generación de reportes PDF (reportlab)
  ui/
    main_window.py           Ventana principal
    equipment_dialog.py       Formulario de captura/edición de equipo
    catalog_dialog.py         Selector y administrador de catálogo
    reference_dialog.py       Ventana de referencia rápida
    unit_converter_dialog.py  Convertidor pies / metros (menú Herramientas)
    diagram_widget.py         Diagrama en vivo del área protegida del equipo
    style.py                  Hoja de estilos Qt (QSS) con la paleta ANSUL
    form_widgets.py           Constructor de formularios dinámicos
android/                      Versión Android (Kivy/KivyMD) — reutiliza ansul/
                               tal cual; main.py es el punto de entrada, ui/
                               trae las pantallas y el formulario dinámico
tests/
  test_engine.py              Pruebas de regresión del motor de cálculo
  _smoke_phase4.py            Prueba de humo de interfaz de escritorio
                               (offscreen, no es parte de la suite automática)
  _smoke_android.py           Prueba de humo de la interfaz Android (requiere
                               Kivy/KivyMD instalados; tampoco es automática)
packaging/windows/            Archivos para generar el instalador de Windows
                               (spec de PyInstaller, script .bat, script de
                               Inno Setup, guía paso a paso)
packaging/android/            Archivos para generar el .apk de Android
                               (buildozer.spec vive en android/, script de
                               build, guía paso a paso)
.github/workflows/            Workflows de GitHub Actions para compilar el
                               instalador de Windows y el .apk de Android
                               en la nube
```

## Pruebas

El motor de cálculo tiene pruebas de regresión que no requieren interfaz
gráfica:

```bash
python tests/test_engine.py
```

## Notas de esta versión

- La lógica de cálculo replica exactamente la de `AnsulCalc.html`, con dos
  correcciones de robustez encontradas durante la portación (documentadas en
  el código): la selección de opción en categorías con varias boquillas
  candidatas (wok, salamandra, parrilla, estufa, plancha) ahora es siempre
  por posición en la lista mostrada — nunca por un índice interno que podía
  quedar desalineado y provocar un error.
- Los ductos de gran tamaño (perímetro > 135 in) usan la misma estimación
  conservadora del original; siga verificando esos casos contra las Gráficas
  4-1/4-2 del manual antes de instalar.
- Los renglones del catálogo con `nozzles: null` (algunos modelos Belshaw,
  Krispy Kreme, Dunkin Donuts, etc.) son de referencia informativa: el
  manual no da una cantidad de boquilla fija para esos modelos porque
  depende de una tabla de espaciado según la longitud del riesgo.
- **Robata**: usa las mismas variantes ya validadas de carbón natural (1N) y
  leña (3N) del manual R-102 (Sección 4), eligiendo el combustible sólido
  correspondiente; no es una tabla nueva, sino la reutilización explícita de
  esas dos variantes bajo una categoría propia.
- **Pleno**: la captura ahora es en metros (longitud y, cuando la variante
  tiene un ancho máximo tabulado, también el ancho); internamente se
  convierte a pies antes de aplicar la fórmula original del manual, que no
  cambió.
- **Selección manual de tanques**: es un complemento a la selección
  automática, no la reemplaza — se activa por sistema. Si el galonaje
  elegido no alcanza el flow number calculado, tanto la vista del sistema
  como el PDF muestran una advertencia; verifique siempre la combinación de
  cartuchos contra la Guía de Selección de Sistema (Sección 9) del manual
  cuando use 3 o más tanques.
- **Modularización automática**: divide el riesgo por su lado más largo en
  N zonas iguales y busca, para el N más pequeño posible, qué boquilla(s)
  cubren una zona — exactamente el método documentado en el manual para
  freidoras (pág. 4-10/4-11) y sartenes de volteo (pág. 4-12, que además
  indica usar el tamaño "con escurridor" para dimensionar cada zona aunque
  el riesgo no tenga escurridor). Para Estufa, Plancha y Parrilla/Robata el
  manual no describe un procedimiento de modularización tan explícito como
  el de freidoras; se aplicó el mismo método por consistencia y sentido de
  ingeniería, así que — igual que con cualquier resultado de esta
  herramienta — verifique el resultado final contra el manual o con ANSUL
  antes de instalar, especialmente en riesgos modularizados en 3 o más
  zonas. La Freidora conserva su tope absoluto de 864 in² (no se puede
  modularizar por encima de ese límite); el Sartén de Volteo no tiene ese
  tope, como indica el manual.
- **Capacidad total de flujo del sistema**: el reporte PDF de cada sistema
  ya mostraba el "flow number" total de ese sistema; ahora el reporte PDF
  de proyecto también incluye la capacidad total de flujo sumando todos
  los sistemas del proyecto.
