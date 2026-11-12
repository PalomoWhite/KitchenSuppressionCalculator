# Kitchen Suppression Calculator

**[Español](#español)** · **[English](#english)**

Calculadora de apoyo para el diseño preliminar de sistemas de supresión de
incendios en cocinas comerciales (ANSUL R-102 y Buckeye Kitchen Mister).
*A preliminary design aid for commercial kitchen fire suppression systems
(ANSUL R-102 and Buckeye Kitchen Mister).*

Autor / Author: **Miguel Alejandro Gutiérrez Torres** · Licencia / License:
[GNU GPL v3.0](LICENSE)

**Descargas / Downloads:** Windows, macOS (Apple Silicon) y Linux en la
sección [Releases](https://github.com/PalomoWhite/KitchenSuppressionCalculator/releases).

---

## Español

Calculadora de apoyo para el diseño preliminar de sistemas de supresión
para cocinas comerciales **ANSUL(R) R-102** y **Buckeye Kitchen Mister**. Para
ANSUL es el equivalente en Python /
PySide6 de la herramienta web `AnsulCalc.html`, con la misma lógica de
cálculo (verificada línea por línea contra el original) y las mismas
funciones: proyectos, sistemas (antes "cocinas"), riesgos (antes "equipos"),
catálogo de 65 modelos por marca, selección de tanques/cartuchos, y
reportes PDF.

> **AVISO IMPORTANTE:** esta aplicación es una **ayuda de diseño preliminar**
> basada en los manuales del fabricante: ANSUL(R) R-102 (Part No. 418087) con
> la Hoja Resumen F-2015158-01_LAS, y Buckeye Kitchen Mister (BFR-TM Rev. 6).
> El diseño final de cualquier sistema debe ser verificado (y, en ANSUL,
> sellado) por un diseñador certificado o distribuidor autorizado de la
> marca, conforme a NFPA 17A y los códigos locales aplicables.

### Marcas soportadas

Al crear un proyecto se elige la marca; todos sus sistemas y riesgos son de
esa marca (no hay proyectos mixtos):

- **ANSUL R-102** — manual R-102 (Part No. 418087) y Hoja Resumen
  F-2015158-01_LAS. Incluye el catálogo de modelos por marca y la selección
  de tanques/cartuchos.
- **Buckeye Kitchen Mister** — manual técnico BFR-TM Rev. 6 (2020-02-01):
  coberturas fijas por equipo (p. 3-12), módulos para equipos grandes
  (p. 3-11), ductos, plenos y precipitadores, y todas las combinaciones
  posibles de cilindros BFR-5/10/15/20 para que el usuario elija.

El diseño (cómo se organiza el código y qué decisiones se tomaron) está en
[`docs/DISEÑO.md`](docs/DISEÑO.md); los datos del manual Buckeye con sus
páginas, en [`docs/inventory_buckeye.md`](docs/inventory_buckeye.md).

### Instalación

Requiere Python 3.9 o superior.

```bash
pip install -r requirements.txt
```

### Ejecutar

```bash
python main.py
```

### Idioma y tema

En **Configuración → Idioma y tema…** se elige el idioma (Español / English) y
el tema (Claro / Oscuro). El tema se aplica al momento; el idioma, al
reiniciar el programa (el diálogo ofrece reiniciar). Los resultados ya
calculados se traducen solos al abrir el proyecto, sin cambiar boquillas ni
flow numbers, y los reportes PDF salen en el idioma activo. La preferencia se
guarda en `settings.json`, junto al archivo de proyectos.

Para probar en otro idioma sin cambiar la configuración:
`ANSULCALC_LANG=en python main.py`.

### Qué hace

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

- Windows/Mac/Linux: `~/Documents/KitchenSuppressionCalculator/ansulcalc_db.json`
  (o `~/Documentos/...` si el sistema está en español). Si ya existe la
  carpeta del nombre anterior del programa (`AnsulFlowCalculator`), se sigue
  usando esa.

### Instalador de Windows

Para distribuir la app a usuarios de Windows sin que necesiten instalar
Python, ver la guía paso a paso en
[`packaging/windows/instalador_windows.md`](packaging/windows/instalador_windows.md)
(incluye una opción para compilarlo en la nube con GitHub Actions si no
tienes una PC con Windows a la mano).

### Estructura del proyecto

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
  settings.py                Configuración (idioma y tema) en settings.json
  i18n.py                    tr(): traduce los textos de la interfaz
  i18n_en.py                 Catálogo de traducciones al inglés
  systems/                   Registro de marcas (ver docs/DISEÑO.md)
    ansul_r102.py            Adaptador de ANSUL R-102 (usa los módulos de arriba)
    buckeye_bfr/             Buckeye Kitchen Mister: data, engine,
                             category_defs y system
  ui/
    main_window.py           Ventana principal
    equipment_dialog.py       Formulario de captura/edición de equipo
    catalog_dialog.py         Selector y administrador de catálogo
    reference_dialog.py       Ventana de referencia rápida (ANSUL)
    buckeye_reference_dialog.py  Referencia rápida Buckeye
    unit_converter_dialog.py  Convertidor pies / metros (menú Herramientas)
    diagram_widget.py         Diagrama en vivo del área protegida del equipo
    style.py                  Hoja de estilos Qt (QSS): paletas clara y oscura
    settings_dialog.py        Diálogo de Configuración (idioma y tema)
    form_widgets.py           Constructor de formularios dinámicos
tests/
  test_engine.py              Pruebas de regresión del motor ANSUL
  test_buckeye.py             Pruebas del motor Buckeye y del registro de marcas
  test_i18n.py                Pruebas de idioma (inglés) y configuración
  _smoke_phase4.py            Prueba de humo de interfaz (ANSUL, offscreen)
  _smoke_buckeye.py           Prueba de humo de interfaz (Buckeye, offscreen)
docs/                         Diseño e inventario técnico Buckeye
packaging/windows/            Archivos para generar el instalador de Windows
                               (spec de PyInstaller, script .bat, script de
                               Inno Setup, guía paso a paso)
packaging/multiplataforma/    Spec de PyInstaller para macOS y Linux
.github/workflows/build.yml   Compila Windows, macOS y Linux en GitHub Actions
                               y publica el Release al subir una etiqueta v*
```

### Pruebas

El motor de cálculo tiene pruebas de regresión que no requieren interfaz
gráfica:

```bash
python -m tests              # todas las pruebas (ANSUL + Buckeye + idioma)
python -m tests.test_engine  # solo ANSUL
python -m tests.test_buckeye # solo Buckeye
python -m tests.test_i18n    # solo idioma y configuración
```

Pruebas de humo de la interfaz (requieren PySide6, no abren ventanas):

```bash
QT_QPA_PLATFORM=offscreen python tests/_smoke_phase4.py
QT_QPA_PLATFORM=offscreen python tests/_smoke_buckeye.py
```

### Notas de esta versión

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

### Autor y licencia

Autor: **Miguel Alejandro Gutiérrez Torres** (proyecto personal, hecho por
su cuenta y con recursos propios).

Este programa es software libre y gratuito, publicado bajo la licencia
**GNU GPL v3.0** (ver [`LICENSE`](LICENSE)): cualquiera puede descargarlo,
usarlo, estudiarlo y modificarlo en su equipo. Si alguien distribuye una
versión modificada, debe publicarla también bajo GPL v3.0, con su código
fuente y conservando el crédito del autor original. Se ofrece **sin ninguna
garantía**.

ANSUL(R) y R-102 son marcas de sus respectivos titulares (Johnson Controls /
Tyco Fire Products); Buckeye Kitchen Mister es marca de Buckeye Fire
Equipment. Este proyecto es independiente: no está afiliado, patrocinado ni
avalado por ninguno de los fabricantes. Los manuales de los fabricantes no
se incluyen en este repositorio.

---

## English

A support calculator for the preliminary design of commercial kitchen fire
suppression systems: **ANSUL(R) R-102** and **Buckeye Kitchen Mister**. For
ANSUL it is the Python / PySide6 equivalent of the `AnsulCalc.html` web tool,
with the same calculation logic (checked line by line against the original)
and the same features: projects, systems (formerly "kitchens"), hazards
(formerly "equipment"), a catalog of 65 models by brand, tank/cartridge
selection, and PDF reports.

> **IMPORTANT NOTICE:** this application is a **preliminary design aid**
> based on the manufacturers' manuals: ANSUL(R) R-102 (Part No. 418087) with
> Summary Sheet F-2015158-01_LAS, and Buckeye Kitchen Mister (BFR-TM Rev. 6).
> The final design of any system must be verified (and, for ANSUL, sealed)
> by a certified designer or authorized distributor of the brand, per
> NFPA 17A and applicable local codes.

### Supported brands

The brand is chosen when a project is created; all its systems and hazards
belong to that brand (no mixed projects):

- **ANSUL R-102** — R-102 manual (Part No. 418087) and Summary Sheet
  F-2015158-01_LAS. Includes the model catalog by brand and tank/cartridge
  selection.
- **Buckeye Kitchen Mister** — BFR-TM technical manual Rev. 6 (2020-02-01):
  fixed coverages per appliance (p. 3-12), modules for large appliances
  (p. 3-11), ducts, plenums and precipitators, and every possible
  combination of BFR-5/10/15/20 cylinders so the user can choose.

The design (how the code is organized and which decisions were made) is in
[`docs/DISEÑO.md`](docs/DISEÑO.md); the Buckeye manual data with its pages is
in [`docs/inventory_buckeye.md`](docs/inventory_buckeye.md) (both in Spanish).

### Installation

Requires Python 3.9 or later.

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Language and theme

In **Settings → Language and theme…** you choose the language (Español /
English) and the theme (Light / Dark). The theme is applied right away; the
language when the program restarts (the dialog offers to restart). Results
already calculated are translated automatically when the project is opened,
without changing nozzles or flow numbers, and PDF reports come out in the
active language. The preference is saved in `settings.json`, next to the
projects file.

To try another language without changing the settings:
`ANSULCALC_LANG=en python main.py`.

### What it does

- **Projects → Systems → Hazards**: organizes the work like the web tool (a
  restaurant can have several systems/hoods, each with its own protected
  hazards/appliances). "System" is the new name for what used to be called
  "Kitchen", and "Hazard" the new name for what used to be called
  "Equipment" — same entity, only the label changed.
- **17 hazard categories**: fryers, tilt skillet, range (1, 2, 4 or 6
  burners), griddle, grill/broiler (gas, electric, charcoal, wood),
  **robata** (1N/3N nozzles for solid fuel — charcoal or wood), chain
  broiler, vertical broiler, salamander, wok, combi oven, **kettle**, duct,
  plenum (in meters) and electrostatic precipitator — each with its own
  form, its **live diagram of the protected area** (drawn as the
  dimensions are entered) and its own calculation logic taken from the
  R-102 manual (Section 4).
- **Combi oven and kettle (no protection required)**: the R-102 manual has
  no standard nozzle for either — the combi oven because it has UL 300-type
  protection inside its closed cabinet, and the kettle because it cooks with
  water/steam (not oil), so it produces no grease vapors. Both are recorded
  in the system for reference only (no nozzles or flow number) so the
  kitchen's appliance count is kept, not because the program can't
  calculate them.
- **Automatic modularization of oversized hazards**: for Fryer, Tilt
  Skillet, Range, Griddle and Grill/Robata, if the hazard is larger than a
  single nozzle covers, the program automatically calculates how many zones
  (modules) are needed and with which nozzle, dividing the hazard along its
  longest side — the same method the R-102 manual uses for fryers and tilt
  skillets (Section 4, pp. 4-10 to 4-12). "Number of modules" can be left at
  1 (automatic) or increased to force more zones than the minimum.
- **Range**: the number of burners (1/2/4/6) and the fuel are informational
  only — the R-102 manual selects nozzles by the cooking area dimensions,
  not by burners, so they don't change the calculation. An oversized
  6-burner range is modularized like any other, showing every applicable
  proximity option (high, medium or low), not a single fixed one.
- **Model catalog by brand**: 65 preloaded entries (Frymaster, Pitco, Henny
  Penny, Garland, Taylor, Nieco, DUKE, Belshaw, etc.) plus your own editable
  catalog (menu **Catalog → Manage my catalog**).
- **Duplicate hazard**: copies an already entered hazard (with its
  dimensions and result) to speed up systems with several identical or very
  similar pieces.
- **Duplicate system**: copies a whole system (name, all its hazards and the
  manual tank override, if any) within the same project.
- **Tank and cartridge selection**: automatic from the system's total flow
  number (1.5 gal, 3 gal, multiple-tank systems), or **manual** (choose how
  many tanks of each size) from the system view — if the manual gallonage
  is not enough for the calculated flow number, the app warns you.
- **"Length x Width" column in the hazards table**: shows the dimensions of
  each hazard at a glance (fryer, tilt skillet, range, griddle,
  grill/broilers/robata: Length x Width; wok and round duct: Ø diameter;
  rectangular duct: Width x Height; plenum: Length x Width in meters). Input
  labels were also unified to "Length (in)" / "Width (in)" for categories
  with a rectangular footprint — the rectangular duct keeps "Width" /
  "Height" because it describes a cross-section, not a footprint.
- **"Depth" column (separate from "Length x Width")**: Wok, Grill, Charcoal
  Broiler, Wood Broiler and Robata also capture a depth (the wok's, or the
  ember/charcoal/wood bed's) that is not part of the area — it has its own
  column in the hazards table. Categories without it show "—".
- **Unit converter** (menu **Tools**): feet ↔ meters. The "Add hazard" form
  also has its own quick converter (meters ↔ feet and inches ↔
  centimeters), right above each category's dimensions.
- **Quotation number**: a project-level field included in the PDF report
  header.
- **PDF reports** per system or for the whole project, with a breakdown of
  hazards, bill of materials, **total flow capacity (flow number)** of the
  system and of the whole project, and the list of required nozzles. The
  generate-PDF button stays disabled until the project/system has hazards,
  and the add-system button until at least one project exists.
- **Backup / restore** of all data in a `.json` file (menu **File**).
- **Quick reference** (menu **Reference**): nozzle table and distribution
  piping requirements by system size, taken from the Summary Sheet.
- **Interface with the web tool's palette** (ANSUL blue `#0554a3`, rounded
  cards) through a Qt style sheet (QSS), plus a dark theme.

Data is saved automatically in:

- Windows/Mac/Linux: `~/Documents/KitchenSuppressionCalculator/ansulcalc_db.json`
  (or `~/Documentos/...` if the system is in Spanish). If the folder of the
  program's previous name (`AnsulFlowCalculator`) already exists, that one
  keeps being used.

### Windows installer

To distribute the app to Windows users without them installing Python, see
the step-by-step guide (in Spanish) in
[`packaging/windows/instalador_windows.md`](packaging/windows/instalador_windows.md)
(it includes an option to build it in the cloud with GitHub Actions if you
don't have a Windows PC at hand).

### Project structure

```
main.py                     Entry point
ansul/
  data.py                   Reference tables (nozzles, fryer groups,
                             grill options, tanks, etc.)
  model_catalog.py           Catalog of 65 brand-specific models
  engine.py                  Calculation engine (1:1 port of AnsulCalc.html)
  category_defs.py           Input field definitions per category
  store.py                   Local JSON persistence (projects/systems/hazards)
  report.py                  PDF report generation (reportlab)
  settings.py                Settings (language and theme) in settings.json
  i18n.py                    tr(): translates the interface texts
  i18n_en.py                 English translation catalog
  systems/                   Brand registry (see docs/DISEÑO.md)
    ansul_r102.py            ANSUL R-102 adapter (uses the modules above)
    buckeye_bfr/             Buckeye Kitchen Mister: data, engine,
                             category_defs and system
  ui/
    main_window.py           Main window
    equipment_dialog.py       Hazard input/edit form
    catalog_dialog.py         Catalog picker and manager
    reference_dialog.py       Quick reference window (ANSUL)
    buckeye_reference_dialog.py  Buckeye quick reference
    unit_converter_dialog.py  Feet / meters converter (Tools menu)
    diagram_widget.py         Live diagram of the protected area
    style.py                  Qt style sheet (QSS): light and dark palettes
    settings_dialog.py        Settings dialog (language and theme)
    form_widgets.py           Dynamic form builder
tests/
  test_engine.py              ANSUL engine regression tests
  test_buckeye.py             Buckeye engine and brand registry tests
  test_i18n.py                Language (English) and settings tests
  _smoke_phase4.py            Interface smoke test (ANSUL, offscreen)
  _smoke_buckeye.py           Interface smoke test (Buckeye, offscreen)
docs/                         Design and Buckeye technical inventory
packaging/windows/            Files to build the Windows installer
                               (PyInstaller spec, .bat script, Inno Setup
                               script, step-by-step guide)
packaging/multiplataforma/    PyInstaller spec for macOS and Linux
.github/workflows/build.yml   Builds Windows, macOS and Linux on GitHub Actions
                               and publishes the Release when a v* tag is pushed
```

The source code (comments, docstrings and interface texts) is written in
Spanish; the English interface comes from `ansul/i18n_en.py`.

### Tests

The calculation engine has regression tests that need no GUI:

```bash
python -m tests              # all tests (ANSUL + Buckeye + language)
python -m tests.test_engine  # ANSUL only
python -m tests.test_buckeye # Buckeye only
python -m tests.test_i18n    # language and settings only
```

Interface smoke tests (require PySide6, open no windows):

```bash
QT_QPA_PLATFORM=offscreen python tests/_smoke_phase4.py
QT_QPA_PLATFORM=offscreen python tests/_smoke_buckeye.py
```

### Notes on this version

- The calculation logic replicates `AnsulCalc.html` exactly, with two
  robustness fixes found during the port (documented in the code): option
  selection in categories with several candidate nozzles (wok, salamander,
  grill, range, griddle) is now always by position in the displayed list —
  never by an internal index that could get out of sync and cause an error.
- Large ducts (perimeter > 135 in) use the same conservative estimate as
  the original; keep checking those cases against Charts 4-1/4-2 of the
  manual before installing.
- Catalog rows with `nozzles: null` (some Belshaw, Krispy Kreme, Dunkin
  Donuts models, etc.) are informational: the manual gives no fixed nozzle
  count for them because it depends on a spacing table by hazard length.
- **Robata**: uses the same already-validated natural charcoal (1N) and wood
  (3N) variants of the R-102 manual (Section 4), choosing the matching solid
  fuel; it is not a new table, just an explicit reuse of those two variants
  under its own category.
- **Plenum**: input is in meters (length and, when the variant has a
  tabulated maximum width, also width); it is converted to feet internally
  before applying the manual's original formula, which did not change.
- **Manual tank selection**: complements automatic selection, it doesn't
  replace it — it is enabled per system. If the chosen gallonage doesn't
  reach the calculated flow number, both the system view and the PDF show a
  warning; always check the cartridge combination against the System
  Selection Guide (Section 9) of the manual when using 3 or more tanks.
- **Automatic modularization**: divides the hazard along its longest side
  into N equal zones and finds, for the smallest possible N, which
  nozzle(s) cover one zone — exactly the method documented in the manual for
  fryers (pp. 4-10/4-11) and tilt skillets (p. 4-12, which also says to use
  the "with drip board" size for each zone even if the hazard has no drip
  board). For Range, Griddle and Grill/Robata the manual doesn't describe a
  modularization procedure as explicit as for fryers; the same method was
  applied for consistency and engineering sense, so — as with any result of
  this tool — verify the final result against the manual or with ANSUL
  before installing, especially for hazards modularized into 3 or more
  zones. The Fryer keeps its absolute cap of 864 in² (it can't be
  modularized beyond that limit); the Tilt Skillet has no such cap, as the
  manual states.
- **Total system flow capacity**: the PDF report of each system already
  showed the system's total flow number; the project PDF report now also
  includes the total flow capacity summing all the project's systems.

### Author and license

Author: **Miguel Alejandro Gutiérrez Torres** (personal project, developed
independently with his own resources).

This program is free software, free of charge, released under the
**GNU GPL v3.0** license (see [`LICENSE`](LICENSE)): anyone can download,
use, study and modify it on their own computer. Anyone who distributes a
modified version must also release it under GPL v3.0, with its source code
and keeping the original author's credit. It is provided **without any
warranty**.

ANSUL(R) and R-102 are trademarks of their respective owners (Johnson
Controls / Tyco Fire Products); Buckeye Kitchen Mister is a trademark of
Buckeye Fire Equipment. This is an independent project: it is not
affiliated with, sponsored or endorsed by any of the manufacturers. The
manufacturers' manuals are not included in this repository.
