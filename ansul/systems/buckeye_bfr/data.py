# -*- coding: utf-8 -*-
"""
Buckeye Kitchen Mister — datos de referencia.

Fuente ÚNICA: manual técnico Buckeye Fire Equipment "Kitchen Mister Restaurant
Cooking Area Fire Suppression System", BPN: BFR-TM, Revisión 6, 2020-02-01
(UL EX 6885). Cada tabla y cada renglón indica la página de donde salió.
Ver también docs/inventory_buckeye.md.

IMPORTANTE: ayuda de diseño PRELIMINAR. El diseño final lo valida un
distribuidor/diseñador autorizado Buckeye (p. 3-1).
"""
from ...i18n import tr

MANUAL = tr('BFR-TM Rev. 6 (2020-02-01)')

# ---- Boquillas (p. 2-9, Figura 2-28; números de parte p. 2-11) -------------
NOZZLES = {
    'N-1HP': {'flow': 1, 'color': tr('Azul'), 'partNo': 'PNZN1HP', 'desc': tr('1 FP — alta proximidad')},
    'N-1LP': {'flow': 1, 'color': tr('Rojo'), 'partNo': 'PNZN1LP', 'desc': tr('1 FP — baja proximidad')},
    'N-2HP': {'flow': 2, 'color': tr('Verde'), 'partNo': 'PNZN2HP', 'desc': tr('2 FP — alta proximidad')},
    'N-2LP': {'flow': 2, 'color': tr('Amarillo'), 'partNo': 'PNZN2LP', 'desc': tr('2 FP — baja proximidad')},
    'N-2W': {'flow': 2, 'color': tr('Blanco'), 'partNo': 'PNZN2W', 'desc': tr('2 FP — gran angular')},
}


def nozzle_flow(code):
    n = NOZZLES.get(code)
    return n['flow'] if n else 0


# ---- Cilindros (p. 2-1, Figura 2-1; números de parte p. 2-10) ---------------
# Cargados con nitrógeno seco a 195 psig @ 70 °F (p. 2-1).
CYLINDERS = {
    5: {'model': 'BFR-5', 'flow': 5, 'partNo': 'BFR5', 'bracket': 'MB-1', 'weight': tr('42 lb (19 kg)'),
        'maxPipeMl': 1500, 'maxPipeBetweenNozzlesMl': 1000, 'maxElbows': 20},
    10: {'model': 'BFR-10', 'flow': 10, 'partNo': 'BFR10', 'bracket': 'MB-2', 'weight': tr('74 lb (33 kg)'),
         'maxPipeMl': 2500, 'maxPipeBetweenNozzlesMl': 2000, 'maxElbows': 25},
    15: {'model': 'BFR-15', 'flow': 15, 'partNo': 'BFR15', 'bracket': 'MB-2', 'weight': tr('107 lb (48 kg)'),
         'maxPipeMl': 2800, 'maxPipe38Ml': 2500, 'maxPipeBetweenNozzlesMl': 2500, 'maxElbows': 25},
    20: {'model': 'BFR-20', 'flow': 20, 'partNo': 'BFR20', 'bracket': 'MB-2', 'weight': tr('130 lb (60 kg)'),
         'maxPipeMl': 2800, 'maxPipe38Ml': 2500, 'maxPipeBetweenNozzlesMl': 2500, 'maxElbows': 25},
}
CYLINDER_SIZES = (5, 10, 15, 20)
CYLINDER_CHARGE = tr('195 psig (1344 kPa) @ 70 °F (21 °C), nitrógeno seco (p. 2-1)')

# ---- Tubería (p. 3-13) ------------------------------------------------------
PIPE_VOLUME_ML_PER_FT = {'3/8': 37.5, '1/2': 59.8}   # (123 / 196 mL/m)
MIN_SYSTEM_FLOW_POINTS = 3
MIN_ELBOWS_BEFORE_FIRST_NOZZLE = 5
MIN_VOLUME_BEFORE_FIRST_NOZZLE_ML = 360
MIN_TOTAL_PIPE_VOLUME_ML = 660
MAX_ELBOWS_BETWEEN_NOZZLES = 5
MAX_SUPPLY_RISE_FT = 10
MAX_NOZZLE_RISE_FT = 2
PIPING_NOTES = [
    tr('Toda la tubería debe ser de 3/8 in (17.1 mm OD) o 1/2 in (21.3 mm OD); volumen: 37.5 '
       'mL/ft (3/8) y 59.8 mL/ft (1/2).'),
    tr('Tubería cédula 40 negra, cromada o de acero inoxidable; conexiones clase 150 lb (p. 2-9 / '
       '3-13).'),
    tr('Máximo 5 codos entre dos boquillas cualesquiera.'),
    tr('Subida vertical máxima de la línea de suministro: 10 ft (3 m) — diferencia de elevación '
       'entre la salida del tanque y la boquilla más alta, o entre la salida del tanque y el '
       'punto más alto o más bajo de la tubería.'),
    tr('Subida vertical máxima de cualquier boquilla sobre la línea de suministro: 2 ft (0.6 m).'),
    tr('No se permiten trampas (tramos donde se pueda acumular líquido: puntos bajos o tubería '
       'que pase de la última boquilla).'),
    tr('Con diámetros distintos, el mayor va más cerca del cilindro y se reduce hacia las '
       'boquillas.'),
    tr('Los codos o adaptadores giratorios para apuntar la boquilla NO cuentan para el total de '
       'codos ni entre boquillas.'),
]
MIN_PIPING_NOTES = [
    tr('Mínimo 5 codos antes de la boquilla más cercana que protege freidora, estufa o wok.'),
    tr('Mínimo 360 mL de tubería antes de esa boquilla.'),
    tr('Volumen total de tubería del sistema: mínimo 660 mL (todos los cilindros).'),
    tr('Mínimo 3 flow points por sistema.'),
]
# Categorías que activan los requisitos mínimos de tubería (p. 3-13: "ONLY apply
# when protecting a wok, deep fat fryer, or range").
MIN_PIPING_CATEGORIES = ('wok', 'fryer', 'range', 'rangegriddle')

# ---- Coberturas de equipos --------------------------------------------------
# w = ancho máximo (de lado a lado), d = fondo máximo (de frente a atrás) del
# área de cocción, tal como lo escribe el texto del manual ("X wide by Y
# deep"). hmin/hmax = altura de la boquilla sobre la superficie de cocción (in).
# backShelf: True = renglón marcado en la tabla p. 3-12 para estufa con
# repisa trasera (* o ***); 'only' = solo aplica con repisa.
RANGE_OPTIONS = [
    {'id': 'R2_LP', 'nozzle': 'N-1LP', 'w': 12, 'd': 24, 'hmin': 16, 'hmax': 30, 'page': '3-3',
     'backShelf': True, 'tag': tr('2 quemadores — baja proximidad'),
     'placement': tr('A 3 in del borde frontal o trasero, sobre la línea central larga; apuntar a 6 in del '
                     'borde opuesto.')},
    {'id': 'R4_HP', 'nozzle': 'N-1LP', 'w': 24, 'd': 24, 'hmin': 30, 'hmax': 40, 'page': '3-4',
     'backShelf': False, 'tag': tr('4 quemadores — alta proximidad'),
     'placement': tr('Dentro de 3 in del centro del equipo; apuntar al centro.')},
    {'id': 'R4_LP', 'nozzle': 'N-2W', 'w': 24, 'd': 24, 'hmin': 16, 'hmax': 30, 'page': '3-4',
     'backShelf': True, 'tag': tr('4 quemadores — baja proximidad'),
     'placement': tr('Al centro del equipo; apuntar al centro.')},
    {'id': 'R6', 'nozzle': 'N-2LP', 'w': 36, 'd': 24, 'hmin': 35, 'hmax': 43, 'page': '3-4',
     'backShelf': False, 'tag': tr('6 quemadores'),
     'placement': tr('Centrada sobre el equipo; apuntar al centro.')},
    {'id': 'R4_BS_HP', 'nozzle': 'N-2LP', 'w': 24, 'd': 24, 'hmin': 30, 'hmax': 40, 'page': '3-6',
     'backShelf': 'only', 'tag': tr('4 quemadores con repisa trasera — alta proximidad'),
     'placement': tr('6 in fuera del borde frontal de los quemadores, dentro de 9 in de la línea central; '
                     'apuntar a 6 in del borde trasero. Repisa: mínimo 16 in sobre el equipo y máximo 11 in '
                     'sobre el borde trasero de los quemadores.')},
]
RANGE_GRIDDLE_OPTIONS = [
    {'id': 'RG', 'nozzle': 'N-1LP', 'w': 30, 'd': 24, 'hmin': 30, 'hmax': 40, 'page': '3-5',
     'tag': tr('Combinación estufa / plancha'),
     'placement': tr('Dentro de 3 in del centro del equipo; apuntar al centro.')},
]
GRIDDLE_OPTIONS = [
    {'id': 'G_STD', 'nozzle': 'N-1LP', 'w': 42, 'd': 30, 'hmin': 24, 'hmax': 48, 'page': '3-7',
     'tag': tr('Estándar'),
     'placement': tr('Directamente sobre el borde del área de cocción; apuntar a 6 in del centro, en línea con '
                     'la boquilla.')},
    {'id': 'G_LG', 'nozzle': 'N-1LP', 'w': 48, 'd': 30, 'hmin': 30, 'hmax': 43, 'page': '3-8',
     'tag': tr('Grande'),
     'placement': tr('Sobre la línea central, 6 in fuera del borde corto; apuntar a 3 in del centro, en línea '
                     'con la boquilla.')},
    {'id': 'G_XL', 'nozzle': 'N-2LP', 'w': 60, 'd': 30, 'hmin': 24, 'hmax': 48, 'page': '3-8',
     'tag': tr('Extra grande'),
     'placement': tr('Directamente sobre el borde del área de cocción; apuntar a 8 in del centro, en línea con '
                     'la boquilla.')},
    {'id': 'G_XLP', 'nozzle': 'N-2W', 'w': 42, 'd': 30, 'hmin': 2, 'hmax': 10, 'page': '3-9',
     'tag': tr('Estándar — extra baja proximidad'),
     'placement': tr('Sobre cualquier esquina, a 45° de la superficie; apuntar sobre la superficie a igual '
                     'distancia de ambos bordes.')},
    {'id': 'G_LP', 'nozzle': 'N-2W', 'w': 60, 'd': 30, 'hmin': 10, 'hmax': 30, 'page': '3-9',
     'tag': tr('Baja proximidad'),
     'placement': tr('De 0 a 3 in fuera del borde corto; apuntar a 1/4 del lado más largo, en línea con la '
                     'boquilla.')},
]
FRYER_OPTIONS = [
    {'id': 'F', 'nozzle': 'N-2HP', 'w': 20.25, 'd': 24, 'hmin': 24, 'hmax': 45, 'page': '3-7',
     'tag': tr('Freidora'),
     'placement': tr('En cualquier punto sobre el área de cocción; apuntar al centro.')},
]
FRYER_MAX_MODULAR_AREA = 864   # in², p. 3-7 y 3-11
TILT_SKILLET_OPTIONS = [
    {'id': 'T', 'nozzle': 'N-2HP', 'w': 20.25, 'd': 24, 'hmin': 24, 'hmax': 45, 'page': '3-7',
     'tag': tr('Sartén de volteo / braising pan (por boquilla)'),
     'placement': tr('En cualquier punto sobre el área de cocción; apuntar al centro de la zona protegida. La '
                     'tapa no debe interferir con la descarga.')},
]
CHARBROILER_OPTIONS = {
    'radiant': {'id': 'C_RAD', 'nozzle': 'N-1HP', 'w': 36, 'd': 24, 'hmin': 30, 'hmax': 48, 'page': '3-9',
                'tag': tr('Radiante'),
                'placement': tr('En cualquier punto sobre la superficie; apuntar al centro.')},
    'lava': {'id': 'C_LAVA', 'nozzle': 'N-2HP', 'w': 24, 'd': 24, 'hmin': 24, 'hmax': 40, 'page': '3-10',
             'tag': tr('Piedra volcánica (lava rock)'),
             'placement': tr('En cualquier punto sobre la superficie; apuntar al centro.')},
    # Solo en la página de detalle 3-11 (no aparece en la tabla resumen 3-12).
    'solid': {'id': 'C_SOLID', 'nozzle': 'N-2HP', 'w': 24, 'd': 24, 'hmin': 24, 'hmax': 40, 'page': '3-11',
              'maxFuelDepth': 6, 'tag': tr('Combustible sólido (Clase "A")'),
              'placement': tr('En cualquier punto sobre la superficie; apuntar al centro. Profundidad máxima del '
                              'combustible: 6 in.')},
}
CHARBROILER_TYPE_LABELS = {'radiant': tr('Radiante'), 'lava': tr('Piedra volcánica (lava rock)'),
                           'solid': tr('Combustible sólido (Clase "A")')}
UPRIGHT_BROILER = {'id': 'UB', 'nozzle': 'N-1LP', 'w': 36, 'd': 24, 'page': '3-10',
                   'tag': tr('Asador vertical / salamandra'),
                   'height': tr('Esquina superior de la cámara de asado'),
                   'placement': tr('En la esquina de la abertura frontal del equipo; apuntar al centro de la parrilla.')}
WOK = {'id': 'WOK', 'nozzle': 'N-1HP', 'diamMin': 12, 'diamMax': 30, 'hmin': 30, 'hmax': 48, 'page': '3-6',
       'tag': tr('Wok'), 'placement': tr('En cualquier punto sobre el área de cocción; apuntar al centro del fondo. La altura se '
                                     'mide desde el fondo del wok.')}

# ---- Ductos (p. 3-1 y 3-2) --------------------------------------------------
# Rectangular/cuadrado: perímetro máximo y lado mayor máximo (rectangular).
# Redondo: circunferencia máxima y diámetro máximo.
DUCT_OPTIONS = [
    {'id': 'D50', 'nozzle': 'N-1LP', 'maxPerimeter': 50, 'maxSide': 16.75, 'maxCircumference': 50,
     'maxDiameter': 16, 'depth': tr('1 a 6 in dentro de la abertura del ducto'), 'page': '3-1'},
    {'id': 'D150', 'nozzle': 'N-2W', 'maxPerimeter': 150, 'maxSide': 50, 'maxCircumference': 150,
     'maxDiameter': 47.5, 'depth': tr('0 a 6 in dentro de la abertura del ducto'), 'page': '3-1'},
]
DUCT_MAX_GRID = 6   # búsqueda de cuadrícula para ductos > 150 in de perímetro

# ---- Plenos (p. 3-3) --------------------------------------------------------
PLENUM = {'nozzle': 'N-1HP', 'maxLengthFt': 12, 'maxWidthFt': 4, 'page': '3-3'}
PLENUM_KINDS = {
    'single': {'label': tr('Banco sencillo de filtros'),
               'placement': tr('2 in del borde trasero del filtro y a 1/3 de la altura del filtro, dentro de 6 in del '
                               'extremo del pleno; apuntar a lo largo del pleno.')},
    'vbank': {'label': tr('Banco en "V"'),
              'placement': tr('Al centro del ancho de la "V" y 1/3 abajo de la altura vertical, dentro de 6 in del '
                              'extremo del pleno; apuntar a lo largo del pleno.')},
}

# --------------------------- Nombres de categorías --------------------------
CATEGORY_LABELS = {
    'fryer': tr('Freidora / Deep Fat Fryer'),
    'tiltskillet': tr('Sartén de Volteo / Tilting Skillet'),
    'range': tr('Estufa / Range'),
    'rangegriddle': tr('Estufa-Plancha / Range-Griddle Combination'),
    'griddle': tr('Plancha / Griddle'),
    'charbroiler': tr('Asador / Charbroiler'),
    'uprightbroiler': tr('Asador Vertical / Upright Broiler (Salamander)'),
    'wok': tr('Wok'),
    'duct': tr('Ducto / Duct'),
    'plenum': tr('Pleno / Plenum'),
    'precipitator': tr('Precipitador Electrostático / Electrostatic Precipitator'),
}
CATEGORY_ORDER = list(CATEGORY_LABELS.keys())

PDF_DISCLAIMER = (
    tr('Reporte generado con Ansul Flow Calculator como ayuda de diseño preliminar con base en el '
       'manual técnico Buckeye Kitchen Mister (BPN: BFR-TM, Rev. 6, 2020-02-01, UL EX 6885). No '
       'sustituye la verificación y responsiva de un distribuidor/diseñador autorizado Buckeye '
       'Fire Equipment conforme a NFPA 17A y los códigos locales aplicables. La tubería, la '
       'detección y el apuntado de boquillas deben verificarse contra el manual antes de instalar.')
)
