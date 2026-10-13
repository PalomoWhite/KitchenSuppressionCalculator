# -*- coding: utf-8 -*-
"""
Ansul Flow Calculator — Datos de referencia del sistema ANSUL(R) R-102.

Este módulo es un puerto directo (1:1) de las tablas de datos que ya estaban
validadas en la herramienta AnsulCalc.html (basadas en el manual ANSUL(R)
R-102, Part No. 418087, y en la Hoja Resumen F-2015158-01_LAS).

IMPORTANTE: esta app es una AYUDA DE DISEÑO PRELIMINAR. El diseño final de
cualquier sistema R-102 debe ser verificado y sellado por un diseñador
certificado ANSUL R-102, conforme a NFPA 17A y los códigos locales
aplicables.
"""

# ---- Tabla 3-2: Nozzle Identification Chart (Sección 3, pág. 3-5) --------
NOZZLES = {
    '1/2N': {'flow': 0.5, 'partNo': '443321', 'label': '1/2N'},
    '1F':   {'flow': 1,   'partNo': '443319', 'label': '1F'},
    '1N':   {'flow': 1,   'partNo': '443317', 'label': '1N'},
    '1W':   {'flow': 1,   'partNo': '443323', 'label': '1W'},
    '2W':   {'flow': 2,   'partNo': '443325', 'label': '2W'},
    '3N':   {'flow': 3,   'partNo': '443327', 'label': '3N'},
    '230':  {'flow': 2,   'partNo': '443329', 'label': '230'},
    '245':  {'flow': 2,   'partNo': '443331', 'label': '245'},
    '260':  {'flow': 2,   'partNo': '443333', 'label': '260'},
    '290':  {'flow': 2,   'partNo': '443335', 'label': '290'},
    '2120': {'flow': 2,   'partNo': '443337', 'label': '2120'},
}


def nozzle_flow(code):
    n = NOZZLES.get(code)
    return n['flow'] if n else 0


# ---- Freidoras: grupos de tamaño máximo (Tabla 4-2, 4-3 y Nozzle
#      Application Chart, pág. 4-7 a 4-11 y 4-29/4-30) ---------------------
# Cada grupo define el tamaño máximo de la tina SIN escurridor (frypot) y,
# si aplica, el tamaño máximo total CON escurridor (overall). Dimensiones
# en pulgadas [profundidad, longitud] (el orden no importa, se evalúan
# ambas orientaciones).
FRYER_GROUPS = [
    {'id': 'A', 'frypot': (14, 15), 'overall': (14, 21), 'opts': [
        {'nozzle': '290', 'hmin': 13, 'hmax': 16, 'tag': 'Baja proximidad'}]},
    {'id': 'B', 'frypot': (14.5, 14), 'overall': (14.5, 26.5), 'opts': [
        {'nozzle': '290', 'hmin': 16, 'hmax': 27, 'tag': 'Media proximidad'}]},
    {'id': 'C', 'frypot': (15, 14), 'overall': (21, 14), 'opts': [
        {'nozzle': '230', 'hmin': 27, 'hmax': 47, 'tag': 'Alta proximidad'},
        {'nozzle': '245', 'hmin': 20, 'hmax': 27, 'tag': 'Media proximidad'}]},
    {'id': 'D', 'frypot': (19.5, 19), 'overall': (25.375, 19.5), 'opts': [
        {'nozzle': '3N', 'hmin': 21, 'hmax': 34, 'tag': 'Alta proximidad'},
        {'nozzle': '290', 'hmin': 13, 'hmax': 16, 'tag': 'Baja proximidad'}]},
    {'id': 'E', 'frypot': (18, 18), 'overall': (18, 27.75), 'opts': [
        {'nozzle': '3N', 'hmin': 25, 'hmax': 35, 'tag': 'Alta proximidad'}]},
    {'id': 'F', 'frypot': (14.5, 16.5), 'overall': (14.5, 26.5), 'opts': [
        {'nozzle': '290', 'hmin': 16, 'hmax': 21, 'tag': 'Alta proximidad'}]},
    {'id': 'G', 'frypot': (6.5, 17), 'overall': (14, 21), 'electric': True, 'opts': [
        {'nozzle': '245', 'hmin': 21, 'hmax': 27, 'tag': 'Media proximidad (vat dividida eléctrica)'},
        {'nozzle': '290', 'hmin': 16, 'hmax': 21, 'tag': 'Alta proximidad (vat dividida eléctrica)'}]},
]
FRYER_MAX_TOTAL_AREA = 864  # in^2, límite absoluto para modularización

# ---- Categorías con formato "lado más largo + área" (Nozzle Application
#      Chart, pág. 4-29 a 4-31) --------------------------------------------
# hmin/hmax = altura de montaje de boquilla sobre la superficie (in).
RANGE_OPTIONS = [
    {'nozzle': '1N', 'qty': 1, 'longSide': 32, 'area': 384, 'hmin': 30, 'hmax': 40, 'tag': 'Alta proximidad'},
    {'nozzle': '1N', 'qty': 1, 'longSide': 24, 'area': 432, 'hmin': 15, 'hmax': 20, 'tag': 'Baja proximidad'},
    {'nozzle': '1F', 'qty': 1, 'longSide': 28, 'area': 336, 'hmin': 40, 'hmax': 48, 'tag': 'Con repisa trasera (backshelf)'},
    {'nozzle': '260', 'qty': 1, 'longSide': 32, 'area': 384, 'hmin': 30, 'hmax': 40, 'tag': 'Con repisa trasera (backshelf)'},
    {'nozzle': '245', 'qty': 1, 'longSide': 28, 'area': 672, 'hmin': 40, 'hmax': 50, 'tag': 'Alta proximidad'},
    {'nozzle': '260', 'qty': 1, 'longSide': 32, 'area': 768, 'hmin': 30, 'hmax': 40, 'tag': 'Media proximidad'},
    {'nozzle': '290', 'qty': 2, 'longSide': 36, 'area': 1008, 'hmin': 15, 'hmax': 20, 'tag': 'Baja proximidad (dos boquillas)'},
]

GRIDDLE_OPTIONS = [
    {'nozzle': '260', 'qty': 1, 'longSide': 48, 'area': 1440, 'hmin': 30, 'hmax': 50, 'tag': 'Alta proximidad (perímetro)'},
    {'nozzle': '290', 'qty': 1, 'longSide': 30, 'area': 720, 'hmin': 30, 'hmax': 50, 'tag': 'Alta proximidad (centro)'},
    {'nozzle': '1N', 'qty': 1, 'longSide': 36, 'area': 1080, 'hmin': 35, 'hmax': 40, 'tag': 'Alta proximidad (perímetro)'},
    {'nozzle': '290', 'qty': 1, 'longSide': 48, 'area': 1440, 'hmin': 20, 'hmax': 30, 'tag': 'Media proximidad'},
    {'nozzle': '1W', 'qty': 1, 'longSide': 26, 'area': 533, 'hmin': 15, 'hmax': 20, 'tag': 'Baja proximidad'},
    {'nozzle': '2W', 'qty': 1, 'longSide': 36, 'area': 1080, 'hmin': 10, 'hmax': 20, 'tag': 'Baja proximidad'},
    {'nozzle': '2120', 'qty': 1, 'longSide': 48, 'area': 1440, 'hmin': 10, 'hmax': 20, 'tag': 'Baja proximidad'},
]

# Variantes de parrilla/asador (Sección 4, pág. 4-24 a 4-27) con el/los
# combustibles a los que aplica cada una.
GRILL_VARIANTS = [
    {'key': 'gasRadiantElectric', 'nozzle': '1N', 'qty': 1, 'longSide': 36, 'area': 864, 'hmin': 15, 'hmax': 40,
     'fuels': ['gas', 'electric'], 'tag': 'Gas-radiante / eléctrico combinado'},
    {'key': 'electric', 'nozzle': '1N', 'qty': 1, 'longSide': 34, 'area': 680, 'hmin': 20, 'hmax': 50,
     'fuels': ['electric'], 'tag': 'Eléctrico'},
    {'key': 'lavaRock', 'nozzle': '1N', 'qty': 1, 'longSide': 24, 'area': 312, 'hmin': 18, 'hmax': 35,
     'maxDepth': 4, 'fuels': ['gas'], 'tag': 'Lava / cerámica'},
    {'key': 'lavaOrCharcoalAlt', 'nozzle': '3N', 'qty': 1, 'longSide': 30, 'area': 720, 'hmin': 14, 'hmax': 40,
     'maxDepth': 4, 'fuels': ['gas', 'charcoal'], 'tag': 'Lava o carbón — mayor cobertura'},
    {'key': 'naturalCharcoal', 'nozzle': '1N', 'qty': 1, 'longSide': 24, 'area': 288, 'hmin': 18, 'hmax': 40,
     'maxDepth': 4, 'fuels': ['charcoal'], 'tag': 'Carbón natural'},
    {'key': 'woodFueled', 'nozzle': '3N', 'qty': 1, 'longSide': 30, 'area': 720, 'hmin': 14, 'hmax': 40,
     'maxDepth': 6, 'maxLogDiameter': 4, 'fuels': ['wood'], 'tag': 'Leña (mezquite)'},
]
FUEL_LABELS = {'gas': 'Gas', 'electric': 'Eléctrico', 'charcoal': 'Carbón', 'wood': 'Leña'}
FUEL_OPTS_GAS_ELECTRIC = [
    {'value': 'gas', 'label': FUEL_LABELS['gas']},
    {'value': 'electric', 'label': FUEL_LABELS['electric']},
]
# Lista completa de combustibles — usada donde el campo es solo informativo
# (p.ej. Estufa/Range) y no debe filtrar las boquillas calculadas.
FUEL_OPTS_ALL = [{'value': k, 'label': v} for k, v in FUEL_LABELS.items()]

WOK_OPTIONS = [
    {'nozzle': '260', 'qty': 1, 'diamMin': 14, 'diamMax': 30, 'depthMin': 3.75, 'depthMax': 8, 'hmin': 35, 'hmax': 45},
    {'nozzle': '1N', 'qty': 1, 'diamMin': 11, 'diamMax': 24, 'depthMin': 3, 'depthMax': 6, 'hmin': 30, 'hmax': 40},
]

CHAIN_BROILER_OPTIONS = {
    'horizontal': {'nozzle': '1N', 'qty': 2, 'maxLength': 43, 'maxWidth': 31, 'hmin': 1, 'hmax': 3,
                   'label': 'Horizontal (2 boquillas 1N)'},
    'overhead': {'nozzle': '1W', 'qty': 2, 'maxLength': 32, 'maxWidth': 34, 'hmin': 10, 'hmax': 26,
                 'label': 'Cenital / overhead (2 boquillas 1W)',
                 'minOpeningRatio': 0.6, 'minOpening': 12},
}

UPRIGHT_BROILER = {'nozzle': '1/2N', 'qty': 2, 'maxLength': 32.5, 'maxWidth': 30,
                    'label': 'Asador vertical / Salamandra (2 boquillas 1/2N)'}

SALAMANDER_OPTIONS = [
    {'id': 'overhead1N', 'nozzle': '1N', 'qty': 1, 'maxWidth': 29, 'maxDepth': 16,
     'label': 'Cenital 1N (6-12 in al frente, 0-12 in de altura)'},
    {'id': 'overhead1F', 'nozzle': '1F', 'qty': 1, 'maxWidth': 31, 'maxDepth': 15,
     'label': 'Cenital 1F (8-12 in al frente, 12-18 in de altura)'},
    {'id': 'local1N', 'nozzle': '1N', 'qty': 1, 'maxWidth': 31, 'maxDepth': 15,
     'label': 'Lateral / local 1N (montada al costado)'},
]

# ---- Ductos (pág. 4-1 a 4-3) ----------------------------------------------
DUCT_OPTIONS = {
    'single1W': {'nozzle': '1W', 'qty': 1, 'maxPerimeter': 50, 'maxDiameter': 16},
    'single2W': {'nozzle': '2W', 'qty': 1, 'maxPerimeter': 100, 'maxDiameter': 32},
    'dual': {'nozzles': [{'code': '1W', 'qty': 1}, {'code': '2W', 'qty': 1}], 'maxPerimeter': 135, 'rectOnly': True},
}

# ---- Plenos (pág. 4-5 a 4-7) ----------------------------------------------
PLENUM_OPTIONS = {
    'vertical1W': {'nozzle': '1W', 'qty': 1, 'coveragePerNozzleFt': 4, 'maxWidthFt': 4,
                   'label': 'Vertical, 1W (4 ft por boquilla)'},
    'horizV1W': {'nozzle': '1W', 'qty': 1, 'coveragePerNozzleFt': 6,
                 'label': 'Horizontal banco "V", 1W (6 ft por boquilla)'},
    'horizSingle1N': {'nozzle': '1N', 'qty': 1, 'coveragePerNozzleFt': 10,
                       'label': 'Horizontal banco sencillo, 1N (10 ft por boquilla)'},
    'horizVbank1N': {'nozzle': '1N', 'qty': 2, 'coveragePerNozzleFt': 10,
                      'label': 'Horizontal banco "V", 1N (2 boquillas cada 10 ft)'},
}

# ---- Tanques y cartuchos (Tank and Cartridge Requirements, pág. 4-77, y
#      System Selection Guide, pág. 9-1 a 9-4) -----------------------------
# Cada tanque de 3 gal aporta 11 "flow numbers" de capacidad y cada tanque
# de 1.5 gal aporta 5. Números de parte de cartucho verificados contra
# ambas tablas del manual R-102 (Rev. 13, 2022-NOV-14).
N2_LT20R = 'LT-20-R (No. 423429)'
N2_LT30R = 'LT-30-R (No. 423435)'
N2_DOUBLE = 'Doble / Double (No. 423493)'
CO2_101_10 = '101-10 (No. 423439)'
CO2_101_20 = '101-20 (No. 423441)'
CO2_101_30 = '101-30 (No. 423443)'
MULTI_CARTRIDGE_NOTE = (
    'Sistema de 3 o más tanques: se arma con un ensamble de liberación regulada '
    '(1 tanque) más actuador(es) regulado(s) adicionales (hasta 3 tanques c/u). '
    'El cartucho de la liberación es LT-20-R (1.5 gal) o LT-30-R (3 gal); cada '
    'actuador usa cartucho Doble (No. 423493) o LT-A-101-30 (No. 423491) según si '
    'los tanques van "manifolded". Existen varias combinaciones válidas — '
    'verifique la combinación exacta para su configuración en la Guía de '
    'Selección de Sistema (Sección 9, pág. 9-1 a 9-4) del manual R-102.'
)

TANK_TABLE_SIMPLE = [
    {'maxFlow': 5, 'tanks': [1.5], 'n2': 'LT-20-R', 'co2': '101-10'},
    {'maxFlow': 11, 'tanks': [3], 'n2': 'LT-30-R', 'co2': '101-20'},
    {'maxFlow': 16, 'tanks': [1.5, 3], 'n2': 'Doble (Double-Tank)', 'co2': '101-30'},
    {'maxFlow': 22, 'tanks': [3, 3], 'n2': 'Doble (Double-Tank)', 'co2': '101-30'},
]

# ---- Requisitos de tubería de distribución (Hoja Resumen F-2015158-01_LAS,
#      pág. 3-4), referencia informativa mostrada en la app -----------------
PIPING_REQUIREMENTS = [
    {
        'system': '5,6 L (1,5 gal.)', 'flowMax': 5,
        'supplyLenFt': 40, 'supplyElevFt': 6, 'supplyElbows90': 9, 'supplyTees': 1,
        'branchLenFt': 6, 'branchElevFt': 4, 'branchElbows90': 4, 'branchTees': 1, 'branchFlowMax': 2,
        'plenumBranchLenFt': 4, 'plenumBranchElevFt': 2, 'plenumBranchElbows90': 4, 'plenumBranchTees': 2, 'plenumBranchFlowMax': 2,
        'ApplianceBranchLenFt': 10, 'ApplianceBranchElevFt': 2, 'ApplianceBranchElbows90': 6, 'ApplianceBranchTees': 3, 'ApplianceBranchFlowMax': 3,
    },
    {
        'system': '11,3 L (3,0 gal.)', 'flowMax': 11,
        'supplyLenFt': 40, 'supplyElevFt': 6, 'supplyElbows90': 9, 'supplyTees': 1,
        'branchLenFt': 8, 'branchElevFt': 4, 'branchElbows90': 4, 'branchTees': 2, 'branchFlowMax': 4,
        'plenumBranchLenFt': 4, 'plenumBranchElevFt': 2, 'plenumBranchElbows90': 4, 'plenumBranchTees': 2, 'plenumBranchFlowMax': 2,
        'ApplianceBranchLenFt': 12, 'ApplianceBranchElevFt': 2, 'ApplianceBranchElbows90': 6, 'ApplianceBranchTees': 4, 'ApplianceBranchFlowMax': 4,
    },
    {
        'system': '22,7 L (6,0 gal.)', 'flowMax': 22,
        'supplyLenFt': 32, 'supplyElevFt': 6, 'supplyElbows90': 8, 'supplyTees': 2,
        'branchLenFt': 8, 'branchElevFt': 4, 'branchElbows90': 4, 'branchTees': 2, 'branchFlowMax': 4,
        'plenumBranchLenFt': 4, 'plenumBranchElevFt': 2, 'plenumBranchElbows90': 4, 'plenumBranchTees': 2, 'plenumBranchFlowMax': 2,
        'ApplianceBranchLenFt': 12, 'ApplianceBranchElevFt': 2, 'ApplianceBranchElbows90': 6, 'ApplianceBranchTees': 4, 'ApplianceBranchFlowMax': 4,
    },
    {
        'system': '34 L (9,0 gal.)', 'flowMax': 11,
        'supplyLenFt': 40, 'supplyElevFt': 6, 'supplyElbows90': 9, 'supplyTees': 1,
        'branchLenFt': 8, 'branchElevFt': 4, 'branchElbows90': 4, 'branchTees': 2, 'branchFlowMax': 4,
        'plenumBranchLenFt': 4, 'plenumBranchElevFt': 2, 'plenumBranchElbows90': 4, 'plenumBranchTees': 2, 'plenumBranchFlowMax': 2,
        'ApplianceBranchLenFt': 12, 'ApplianceBranchElevFt': 2, 'ApplianceBranchElbows90': 6, 'ApplianceBranchTees': 4, 'ApplianceBranchFlowMax': 4,
    },
]
PIPING_GENERAL_NOTES = [
    'Toda la tubería del sistema R-102 es recta. Se reduce la necesidad de longitudes y equilibrios críticos.',
    'Dos codos de 45° equivalen a uno de 90°.',
    'Cada ramal incluye el tubo en T o el codo que llega a él, y todos los racores que contiene el ramal.',
    'La longitud de tubería mínima de cédula 40, de tubo de 9,5 mm (3/8 pulg.) desde la salida del tanque a '
    'cualquier boquilla de protección de fogón, freidora o wok debe ser de 1,8 m (6 pies).',
    'Las longitudes de tubo se miden desde el centro de un racor al centro de otro.',
    'Toda la tubería de distribución debe ser cédula 40 de hierro negro, cromada o de acero inoxidable. '
    'No utilice tubos galvanizados por inmersión en caliente en la tubería de distribución.',
    'Todas las conexiones roscadas situadas dentro y por encima de la zona protegida deben estar selladas con '
    'cinta para tubos, aplicada solo a las roscas macho, sin cubrir el extremo de la rosca.',
]

# --------------------------- Nombres bilingües -----------------------------
CATEGORY_LABELS = {
    'fryer': 'Freidora / Fryer',
    'tiltskillet': 'Sartén de Volteo / Tilting Skillet',
    'range': 'Estufa / Range',
    'griddle': 'Plancha / Griddle',
    'grill': 'Parrilla / Grill',
    'naturalcharcoal': 'Asador Carbón / Natural Charcoal Grill',
    'woodgrill': 'Asador Leña / Wood Fuel Grill',
    'robata': 'Robata / Robata Grill',
    'chainbroiler': 'Asador de Cadena / Chain Broiler',
    'uprightbroiler': 'Asador Vertical / Upright Broiler',
    'salamander': 'Salamandra / Cheesemelter',
    'wok': 'Wok / Wok',
    'combioven': 'Horno Combi / Combi Oven',
    'kettle': 'Marmita / Kettle',
    'duct': 'Ducto / Duct',
    'plenum': 'Pleno / Plenum',
    'precipitator': 'Precipitador Electrostático / Electrostatic Precipitator',
}
CATEGORY_ORDER = list(CATEGORY_LABELS.keys())

# Categorías renombradas en versiones anteriores — compatibilidad hacia atrás.
LEGACY_CATEGORY_MAP = {'charbroiler': 'chainbroiler'}

# --------------------------- Constantes de reporte PDF ---------------------
PDF_MARGIN = 46
PDF_LINE = 13
PDF_CELL_GAP = 6
PDF_NOZZLE_COLS = [
    {'label': 'Boquilla (modelo)', 'width': 1.6},
    {'label': 'No. de parte', 'width': 1.3},
    {'label': 'Cantidad', 'width': 1, 'num': True},
]
PDF_DISCLAIMER = (
    'Reporte generado con Ansul Flow Calculator como ayuda de diseño preliminar con base en el manual '
    'ANSUL(R) R-102 (Part No. 418087). No sustituye la verificación, sello y responsiva de un diseñador '
    'certificado ANSUL R-102 conforme a NFPA 17A y los codigos locales aplicables. Verifique '
    'especificaciones especificas por marca/modelo de equipo antes de instalar.'
)
