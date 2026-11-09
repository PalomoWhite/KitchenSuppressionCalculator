# Diseño — Soporte para varias marcas (ANSUL R-102 + Buckeye Kitchen Mister)

Este documento describe cómo está organizado el programa para manejar más de
un sistema de supresión, y deja escritas las decisiones que se tomaron (y las
que siguen pendientes) para no tener que redescubrirlas después.

> El programa es una **ayuda de diseño preliminar**. El diseño final de
> cualquier sistema lo valida un diseñador certificado de la marca.

---

## 1. Regla principal: la marca se elige al crear el PROYECTO

- Cada proyecto guarda `'system': 'ansul_r102'` o `'system': 'buckeye_bfr'`.
- **No hay proyectos mixtos**: todos los sistemas y riesgos de un proyecto son
  de la misma marca (los precios y los componentes cambian entre marcas).
- Un proyecto guardado antes de esta versión no tiene la llave `system`: al
  abrir el archivo (`Store.load()`) se le asigna `ansul_r102` y se guarda.
- La marca solo se puede cambiar si el proyecto **todavía no tiene riesgos**
  (`Store.set_project_system()` lanza `ValueError` en caso contrario).

## 2. Diferencias que afectan el código

| Tema | ANSUL R-102 | Buckeye Kitchen Mister |
|---|---|---|
| Capacidad de boquillas | *flow numbers* (0.5, 1, 2, 3) | *flow points* (1 o 2), p. 2-9 |
| Coberturas | lado mayor + área, cajas por grupo (freidoras), etc. | **coberturas fijas por tipo de equipo** (ancho × fondo), p. 3-12 |
| Equipos grandes | modularización por lado mayor | módulos iguales, cada uno ≤ cobertura de una boquilla, p. 3-11 |
| Tanques | 1.5 gal (5 FN) y 3 gal (11 FN) + cartuchos | cilindros BFR-5/10/15/20 = 5/10/15/20 flow points, p. 2-1 |
| Tubería | longitudes y codos por tramo | volumen en mL y codos, p. 3-13 |

**Nunca se suman flow numbers de ANSUL con flow points de Buckeye.** Esto lo
garantiza la regla 1: cada resumen (sistema o proyecto) se calcula con el motor
de la marca del proyecto. En el JSON, el resultado de cada riesgo sigue usando
la llave `flowNumber` (por compatibilidad con los archivos existentes); en un
proyecto Buckeye ese número son *flow points*.

## 3. Organización del código ("el molde")

```
ansul/
  data.py, engine.py, category_defs.py, model_catalog.py   ← ANSUL R-102 (sin cambios)
  systems/
    __init__.py        ← registro (registry): get(key), for_project(p), CHOICES
    base.py            ← clase SystemDef: la "interfaz" que toda marca cumple
    ansul_r102.py      ← adaptador: envuelve los módulos ANSUL existentes
    buckeye_bfr/
      data.py          ← tablas del manual BFR-TM Rev. 6 (cada dato con su página)
      engine.py        ← cálculo de coberturas, módulos, ductos, plenos y cilindros
      category_defs.py ← campos de captura por categoría (mismo formato que ANSUL)
      system.py        ← SystemDef de Buckeye
```

Decisión: los archivos de ANSUL **no se movieron** de lugar. Moverlos solo
cambiaba rutas de `import` en todo el programa y en las pruebas, con riesgo y
sin beneficio. El adaptador `ansul_r102.py` los expone con la misma interfaz
que Buckeye.

### Lo que expone cada marca (`SystemDef`)
- `key`, `label`, `flow_label` ("Flow number" / "Flow points").
- `category_order`, `category_labels`, `category_defs`, `has_required_inputs`.
- `category_display_label(item)`, `dimensions_display(item)`, `depth_display(item)`.
- `nozzle_columns()` / `nozzle_row(code, qty)` para las tablas de boquillas.
- `kitchen_summary(kitchen)`, `project_summary(project)`.
- `summary_rows(summary)` (resumen de materiales del sistema) y
  `project_rows(project_summary)` — los usan la pantalla y el PDF.
- `diagram_spec(category, values)` para el diagrama en vivo.
- `supports_catalog`, `supports_tank_override`, `supports_cylinder_choice`.
- `report_subtitle`, `disclaimer`, `disclaimer_short`.

La interfaz (ventana principal, formulario de riesgos, referencia) y el reporte
PDF piden todo a la marca del proyecto a través del registro.

## 4. Buckeye — decisiones de cálculo

### 4.1 Coberturas de equipos (p. 3-3 a 3-12)
- Se captura el **área de cocción** (no el tamaño exterior del equipo, p. 3-3):
  **ancho** (de lado a lado) y **fondo** (de frente a atrás).
- Cada opción de boquilla se compara con su cobertura tal como la escribe el
  texto del manual: "X wide by Y deep" → ancho ≤ X **y** fondo ≤ Y.
- Se muestran **todas** las opciones que aplican (por ejemplo, una estufa de
  24 × 24 puede ir con N-1LP alta proximidad, N-2W baja proximidad, o dos N-1LP
  de 12 × 24), ordenadas por flow points totales. El usuario elige.

### 4.2 Equipos con varias boquillas (módulos, p. 3-11)
- El área se divide en una cuadrícula de módulos **iguales**:
  `columnas = ⌈ancho / ancho_cobertura⌉`, `filas = ⌈fondo / fondo_cobertura⌉`.
  Es el menor número de módulos iguales que cumple "cada módulo ≤ cobertura de
  una boquilla".
- Freidoras: si se necesita más de un módulo y el área es mayor a **864 in²**,
  no se puede modularizar (p. 3-7 y 3-11).
- Wok, salamandra (upright broiler), ductos redondos: no se modularizan.
- Ductos rectangulares de más de 150 in de perímetro: varias N-2W, dividiendo
  la sección en áreas iguales y simétricas (p. 3-2) — se busca la cuadrícula
  con menos boquillas en la que cada área cumple perímetro ≤ 150 in y lado
  mayor ≤ 50 in.
- Plenos: una N-1HP por cada tramo de 12 ft (se recomiendan tramos iguales,
  p. 3-3); ancho máximo 4 ft.

### 4.3 Selección de cilindros
- Capacidad: BFR-5/10/15/20 = 5/10/15/20 flow points (p. 2-1).
- **El programa muestra todas las combinaciones mínimas** y el usuario elige
  (decisión de Miguel: no se sabe qué necesite el cliente o la obra; aunque es
  raro, a veces sí se instalan cilindros de 15 o 20).
- Combinación válida = alcanza para las boquillas **y** si se le quita
  cualquier cilindro ya no alcanza (así no aparecen cilindros de sobra).
- "Alcanza" considera que una boquilla de 2 flow points no se puede partir
  entre dos cilindros: con `n1` boquillas de 1 FP y `n2` de 2 FP, la
  combinación de capacidades `c` alcanza si
  `n2 ≤ Σ⌊cᵢ/2⌋` y `n1 + 2·n2 ≤ Σcᵢ`.
  (Ejemplo: 5 boquillas N-2HP = 10 FP **no** caben en 2 × BFR-5, porque cada
  BFR-5 solo acepta 2 boquillas de 2 FP.)
- Orden de la lista: primero menor sobrante de flow points, después menos
  cilindros. La combinación elegida se guarda en el sistema
  (`kitchen['cylinderChoice']`, p. ej. `[10, 10, 5]`). Si después cambian los
  riesgos y esa combinación ya no es válida, se usa la primera de la lista y
  se avisa.
- Mínimo 3 flow points por sistema y requisitos mínimos de tubería (5 codos,
  360 mL antes de la primera boquilla, 660 mL totales): según el criterio de
  Miguel, los cuatro aplican **solo** cuando el sistema protege wok, freidora
  o estufa (p. 3-13). El programa los muestra como aviso en ese caso.
- La tubería no se calcula (no se capturan longitudes). El resumen muestra
  los volúmenes máximos de tubería del cilindro elegido como referencia.

## 5. Pendientes / dudas para confirmar ⚠️

1. **Orientación de las coberturas.** El texto dice "X wide by Y deep", pero
   algunas figuras rotulan al revés (p. ej. freidora, Fig. 3-15: "max. width
   24, max. length 20.25"). Hoy el programa NO rota la cobertura (opción
   conservadora). Confirmar con el distribuidor si se puede girar.
2. **Ducto redondo de 50 in / 16 in.** El manual da 50 in de circunferencia
   "[16 in de diámetro]", pero π × 16 = 50.3 in. El programa exige ambas
   condiciones (diámetro ≤ 15.9 in en la práctica).
3. **Asador de combustible sólido (Class "A")**: viene en la p. 3-11 pero no en
   la tabla resumen de la p. 3-12. Se incluyó con los datos de la p. 3-11.
4. **Estufa con repisa trasera**: el programa ofrece solo los renglones que la
   tabla marca para repisa (2 quemadores y 4 quemadores baja proximidad, `*`;
   4 quemadores alta proximidad con repisa, `***`).
5. **Más módulos de los mínimos**: en Buckeye no hay campo para forzar más
   módulos (en ANSUL sí). Agregarlo si hace falta.
