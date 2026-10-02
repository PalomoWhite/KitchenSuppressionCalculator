# -*- coding: utf-8 -*-
"""
Definición declarativa de los campos de captura y el cálculo asociado a
cada categoría de equipo. Es el equivalente en Python del objeto
CATEGORY_DEF de AnsulCalc.html, pero en vez de generar HTML describe los
campos de forma neutral (tipo, etiqueta, opciones) para que la interfaz
PySide6 construya el formulario dinámicamente.

Tipos de campo soportados por la UI (ver ansul/ui/equipment_dialog.py):
  - 'number'  : captura numérica (float)
  - 'select'  : lista de opciones {value,label}
  - 'toggle'  : casilla de verificación (bool)
  - 'info'    : texto informativo, sin captura

Cada definición de categoría expone:
  fields(values)            -> lista de descriptores de campo a mostrar
                                (algunos campos son condicionales, p.ej. el
                                tamaño "con escurridor" de una freidora solo
                                aparece si hasDripboard=True)
  required_fields(values)   -> claves de campo obligatorias para calcular
  compute(values)           -> corre el motor de cálculo y regresa el dict
                                crudo (con 'ok' y, si aplica, 'matches')
  has_choice                -> True si compute() regresa opciones para que
                                el usuario elija una (choice_label/choice_sub
                                describen cada opción)
  result_from_choice(calc, idx) -> arma el resultado final una vez elegida
                                una opción (solo si has_choice)
  not_fit_msg(values, calc) -> mensaje a mostrar cuando ok=False
"""
from . import data as D
from . import engine as E


def _num(v):
    return E.num(v)


def _module_suffix(m):
    """Texto adicional para choice_label cuando el resultado viene de una
    modularización automática (o forzada) en más de una zona — ver
    E._modularize_long_side_area / E._modularize_box en engine.py."""
    n = m.get('modulesCount', 1)
    if n <= 1:
        return ''
    per_module_qty = m.get('qty', 1)
    total = per_module_qty * n
    plural = 's' if total != 1 else ''
    return f" · modularizado en {n} zonas (total {total} boquilla{plural} {m['nozzle']})"


# --------------------------------------------------------------------------
# Freidora
# --------------------------------------------------------------------------

def _fryer_fields(v):
    fields = [
        {'key': 'fuel', 'type': 'select', 'label': 'Combustible',
         'options': D.FUEL_OPTS_GAS_ELECTRIC, 'default': 'gas'},
        {'key': 'hasDripboard', 'type': 'toggle', 'label': '¿Tiene escurridor (dripboard)?', 'default': False,
         'reflow': True},
        {'key': 'frypotD', 'type': 'number', 'label': 'Largo de la tina (in)', 'hint': 'De frente a fondo'},
        {'key': 'frypotL', 'type': 'number', 'label': 'Ancho de la tina (in)', 'hint': 'De lado a lado'},
    ]
    if v.get('hasDripboard'):
        fields += [
            {'key': 'overallD', 'type': 'number', 'label': 'Largo total con escurridor (in)'},
            {'key': 'overallL', 'type': 'number', 'label': 'Ancho total con escurridor (in)'},
        ]
    fields.append({'key': 'modules', 'type': 'number', 'label': 'Número de módulos (opcional)', 'default': 1, 'required': False,
                    'hint': 'Deje el valor en 1: si la freidora es más grande de lo que cubre una sola boquilla, '
                            'el programa calcula automáticamente cuántos módulos (zonas) se necesitan y con qué '
                            'boquilla, dividiendo el riesgo según el método del manual (pág. 4-10 a 4-12). Aumente '
                            'el número solo si quiere forzar más zonas de las mínimas necesarias. Máx. 864 in² de '
                            'área total (freidora, no aplica a sartén de volteo).'})
    return fields


def _fryer_compute(v):
    return E.calc_fryer(bool(v.get('hasDripboard')), _num(v.get('frypotD')), _num(v.get('frypotL')),
                         _num(v.get('overallD')), _num(v.get('overallL')), v.get('modules') or 1,
                         v.get('fuel') or 'gas')


def _fryer_not_fit(v, c):
    if c.get('overLimit'):
        return (f"El área total ({E.fmt_num(c['totalArea'])} in²) excede el máximo modularizable de 864 in². "
                'Divídalo en riesgos independientes (esa área no se puede cubrir ni modularizando).')
    return (f'Ninguna boquilla estándar cubre estas dimensiones, ni modularizando hasta {E.MAX_AUTO_MODULES} zonas. '
            'Revise las medidas o consulte a ANSUL.')


# --------------------------------------------------------------------------
# Sartén de volteo (Tilting Skillet)
# --------------------------------------------------------------------------

def _tiltskillet_fields(v):
    return [
        {'key': 'd1', 'type': 'number', 'label': 'Ancho (in)', 'hint': 'De lado a lado'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo (in)', 'hint': 'De frente a fondo'},
        {'key': 'modules', 'type': 'number', 'label': 'Número de módulos (opcional)', 'default': 1, 'required': False,
         'hint': 'Deje el valor en 1: el programa divide automáticamente el sartén en tantas zonas (módulos) como '
                 'se necesiten según el número de boquillas requerido (no aplica el límite de 864 in² de la '
                 'freidora). Aumente el número solo si quiere forzar más zonas de las mínimas necesarias.'},
    ]


# --------------------------------------------------------------------------
# Estufa (Range)
# --------------------------------------------------------------------------

def _range_fields(v):
    return [
        {'key': 'burners', 'type': 'select', 'label': 'Número de quemadores (informativo)',
         'options': [{'value': '1', 'label': '1 quemador'}, {'value': '2', 'label': '2 quemadores'},
                     {'value': '4', 'label': '4 quemadores'}, {'value': '6', 'label': '6 quemadores'}],
         'default': '4', 'required': False,
         'hint': 'Solo de referencia: el manual R-102 no distingue boquillas por número de quemadores, sino por '
                 'las medidas del área de cocción — no cambia el cálculo.'},
        {'key': 'fuel', 'type': 'select', 'label': 'Combustible (informativo)', 'options': D.FUEL_OPTS_ALL,
         'default': 'gas', 'required': False,
         'hint': 'Solo de referencia: no cambia el cálculo de boquillas, que depende únicamente de las medidas.'},
        {'key': 'd1', 'type': 'number', 'label': 'Ancho del área de cocción (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo del área de cocción (in)'},
        {'key': 'modules', 'type': 'number', 'label': 'Número de módulos (opcional)', 'default': 1, 'required': False,
         'hint': 'Deje el valor en 1: si la estufa es más grande de lo que cubre una sola boquilla (por ejemplo, '
                 'una de 6 quemadores), el programa modulariza automáticamente el riesgo en tantas zonas como se '
                 'necesiten y muestra todas las opciones de boquilla que apliquen (alta, media o baja '
                 'proximidad) — no solo una fija. Aumente el número solo si quiere forzar más zonas de las '
                 'mínimas necesarias.'},
    ]


def _range_compute(v):
    return E.calc_long_side_area(D.RANGE_OPTIONS, _num(v.get('d1')), _num(v.get('d2')), v.get('modules') or 1)


# --------------------------------------------------------------------------
# Plancha (Griddle)
# --------------------------------------------------------------------------

def _griddle_fields(v):
    return [
        {'key': 'd1', 'type': 'number', 'label': 'Ancho de la superficie (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo de la superficie (in)'},
        {'key': 'modules', 'type': 'number', 'label': 'Número de módulos (opcional)', 'default': 1, 'required': False,
         'hint': 'Deje el valor en 1: el programa modulariza automáticamente una plancha sobredimensionada. '
                 'Aumente el número solo si quiere forzar más zonas de las mínimas necesarias.'},
    ]


# --------------------------------------------------------------------------
# Parrilla / Grill (gas o eléctrica)
# --------------------------------------------------------------------------

_MODULES_FIELD = {'key': 'modules', 'type': 'number', 'label': 'Número de módulos (opcional)', 'default': 1, 'required': False,
                   'hint': 'Deje el valor en 1: el programa modulariza automáticamente un riesgo sobredimensionado. '
                           'Aumente el número solo si quiere forzar más zonas de las mínimas necesarias.'}


def _grill_fields(v):
    return [
        {'key': 'fuel', 'type': 'select', 'label': 'Combustible', 'options': D.FUEL_OPTS_GAS_ELECTRIC, 'default': 'gas'},
        {'key': 'd1', 'type': 'number', 'label': 'Ancho de la parrilla (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo de la parrilla (in)'},
        {'key': 'depth', 'type': 'number', 'label': 'Profundidad de la cama de lava/cerámica (in, opcional)',
         'required': False, 'hint': 'Solo aplica a variantes con lava rock/cerámica'},
        dict(_MODULES_FIELD),
    ]


def _grill_compute(v):
    depth = v.get('depth')
    return E.calc_grill(v.get('fuel') or 'gas', _num(v.get('d1')), _num(v.get('d2')),
                         _num(depth) if depth not in (None, '') else None, v.get('modules') or 1)


# --------------------------------------------------------------------------
# Asador de carbón natural / de leña (usan calc_grill con combustible fijo)
# --------------------------------------------------------------------------

def _naturalcharcoal_fields(v):
    return [
        {'key': 'd1', 'type': 'number', 'label': 'Ancho del asador (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo del asador (in)'},
        {'key': 'depth', 'type': 'number', 'label': 'Profundidad del carbón (in, opcional)', 'required': False},
        dict(_MODULES_FIELD),
    ]


def _woodgrill_fields(v):
    return [
        {'key': 'd1', 'type': 'number', 'label': 'Ancho del asador (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo del asador (in)'},
        {'key': 'depth', 'type': 'number', 'label': 'Profundidad de la leña (in, opcional)', 'required': False},
        dict(_MODULES_FIELD),
    ]


# --------------------------------------------------------------------------
# Robata (asador de combustible sólido — usa las variantes 1N/3N de
# calc_grill ya validadas para carbón natural y leña, Sección 4, pág. 4-24
# a 4-27 del manual R-102)
# --------------------------------------------------------------------------

def _robata_fields(v):
    return [
        {'key': 'fuel', 'type': 'select', 'label': 'Combustible sólido',
         'options': [{'value': 'charcoal', 'label': D.FUEL_LABELS['charcoal']},
                     {'value': 'wood', 'label': D.FUEL_LABELS['wood']}],
         'default': 'charcoal'},
        {'key': 'd1', 'type': 'number', 'label': 'Ancho del robata (in)'},
        {'key': 'd2', 'type': 'number', 'label': 'Largo del robata (in)'},
        {'key': 'depth', 'type': 'number', 'label': 'Profundidad del carbón/leña (in, opcional)', 'required': False,
         'hint': 'Para leña, verifique también el diámetro máximo de troza (4 in) en el detalle del resultado.'},
        dict(_MODULES_FIELD),
    ]


def _robata_compute(v):
    fuel = v.get('fuel') or 'charcoal'
    depth = v.get('depth')
    return E.calc_robata(fuel, _num(v.get('d1')), _num(v.get('d2')),
                          _num(depth) if depth not in (None, '') else None, v.get('modules') or 1)


# --------------------------------------------------------------------------
# Horno combi (informativo, sin boquillas estándar)
# --------------------------------------------------------------------------

def _combioven_fields(v):
    return [{'key': '_info', 'type': 'info',
             'label': 'El manual R-102 no incluye una boquilla estándar para hornos combi con gabinete cerrado '
                       '(protección tipo UL 300 dentro del gabinete). Este renglón se registra solo como '
                       'referencia — no aporta boquillas ni flow number. Si el gabinete permanece abierto '
                       'durante la cocción, consulte a ANSUL para una aplicación específica.'}]


def _combioven_compute(v):
    return {'ok': True, 'result': {'nozzles': [], 'flowNumber': 0,
                                    'detail': 'Horno Combi — no cubierto por el catálogo estándar R-102 (informativo).',
                                    'heightRange': '—'}}


# --------------------------------------------------------------------------
# Marmita (informativo, no requiere protección — no genera vapores
# grasosos como una freidora o parrilla)
# --------------------------------------------------------------------------

def _kettle_fields(v):
    return [{'key': '_info', 'type': 'info',
             'label': 'La marmita (kettle) no requiere protección bajo el manual R-102: al cocinar con agua/vapor '
                       '(no con aceite) no genera vapores grasosos, así que no está listada en el catálogo de '
                       'boquillas. Este renglón se registra solo como referencia — no aporta boquillas ni flow '
                       'number. Si la marmita se usa para freír o genera grasa, consulte a ANSUL para una '
                       'aplicación específica.'}]


def _kettle_compute(v):
    return {'ok': True, 'result': {'nozzles': [], 'flowNumber': 0,
                                    'detail': 'Marmita — no requiere protección bajo el catálogo estándar R-102 (informativo).',
                                    'heightRange': '—'}}


# --------------------------------------------------------------------------
# Asador de cadena (Chain Broiler)
# --------------------------------------------------------------------------

def _chainbroiler_fields(v):
    kind = v.get('kind') or 'horizontal'
    fields = [
        {'key': 'kind', 'type': 'select', 'label': 'Tipo de protección',
         'options': [{'value': 'horizontal', 'label': D.CHAIN_BROILER_OPTIONS['horizontal']['label']},
                     {'value': 'overhead', 'label': D.CHAIN_BROILER_OPTIONS['overhead']['label']}],
         'default': 'horizontal', 'reflow': True},
        {'key': 'length', 'type': 'number', 'label': 'Largo interno (in)', 'hint': 'De frente a fondo, dentro de la cámara'},
        {'key': 'width', 'type': 'number', 'label': 'Ancho interno (in)', 'hint': 'De lado a lado, dentro de la cámara'},
    ]
    if kind == 'overhead':
        fields += [
            {'key': 'openingL', 'type': 'number', 'label': 'Abertura — largo (in)', 'required': False},
            {'key': 'openingW', 'type': 'number', 'label': 'Abertura — ancho (in)', 'required': False,
             'hint': 'Opcional: valida la regla del 60% mínimo de abertura.'},
        ]
    return fields


def _chainbroiler_compute(v):
    kind = v.get('kind') or 'horizontal'
    ol, ow = v.get('openingL'), v.get('openingW')
    return E.calc_chain_broiler(kind, _num(v.get('length')), _num(v.get('width')),
                                 _num(ol) if ol else None, _num(ow) if ow else None)


def _chainbroiler_not_fit(v, c):
    opt = c['opt']
    return (f"Excede el tamaño máximo interno ({opt['maxLength']} × {opt['maxWidth']} in) para esta variante. "
            'Pruebe la otra variante o proteja como riesgos separados.')


# --------------------------------------------------------------------------
# Asador vertical (Upright Broiler)
# --------------------------------------------------------------------------

def _uprightbroiler_fields(v):
    return [
        {'key': 'length', 'type': 'number', 'label': 'Largo interno (in)', 'hint': 'De frente a fondo, dentro de la cámara'},
        {'key': 'width', 'type': 'number', 'label': 'Ancho interno (in)', 'hint': 'De lado a lado, dentro de la cámara'},
    ]


def _uprightbroiler_not_fit(v, c):
    ub = D.UPRIGHT_BROILER
    return f"Excede el máximo estándar ({ub['maxLength']} × {ub['maxWidth']} in). Consulte a ANSUL para aplicación específica."


# --------------------------------------------------------------------------
# Salamandra
# --------------------------------------------------------------------------

def _salamander_fields(v):
    return [
        {'key': 'length', 'type': 'number', 'label': 'Largo interno (in)', 'hint': 'De frente a fondo'},
        {'key': 'width', 'type': 'number', 'label': 'Ancho interno (in)', 'hint': 'De lado a lado'},
    ]


def _salamander_compute(v):
    return E.calc_salamander(_num(v.get('length')), _num(v.get('width')))


# --------------------------------------------------------------------------
# Wok
# --------------------------------------------------------------------------

def _wok_fields(v):
    return [
        {'key': 'diam', 'type': 'number', 'label': 'Diámetro del wok (in)', 'hint': 'Diámetro superior, boca del wok'},
        {'key': 'depth', 'type': 'number', 'label': 'Profundidad del wok (in)', 'hint': 'Del borde superior al fondo'},
    ]


def _wok_compute(v):
    return E.calc_wok(_num(v.get('diam')), _num(v.get('depth')))


# --------------------------------------------------------------------------
# Ducto
# --------------------------------------------------------------------------

def _duct_fields(v):
    is_round = bool(v.get('round'))
    fields = [{'key': 'round', 'type': 'toggle', 'label': 'Ducto redondo', 'default': False, 'reflow': True}]
    if is_round:
        fields.append({'key': 'diameter', 'type': 'number', 'label': 'Diámetro (in)'})
    else:
        fields += [
            {'key': 'sideA', 'type': 'number', 'label': 'Ancho del ducto (in)'},
            {'key': 'sideB', 'type': 'number', 'label': 'Alto del ducto (in)'},
        ]
    fields.append({'key': 'qty', 'type': 'number', 'label': 'Cantidad de ductos idénticos', 'default': 1,
                    'hint': 'Las boquillas se multiplican por esta cantidad si hay más de un ducto igual en el sistema.'})
    return fields


def _duct_required(v):
    return ['diameter'] if v.get('round') else ['sideA', 'sideB']


def _duct_compute(v):
    is_round = bool(v.get('round'))
    perimeter = None if is_round else 2 * ((_num(v.get('sideA')) or 0) + (_num(v.get('sideB')) or 0))
    r = E.calc_duct(perimeter, _num(v.get('diameter')) if is_round else None, is_round, v.get('qty') or 1)
    if r.get('ok'):
        r['result'] = {'nozzles': r['nozzles'], 'flowNumber': r['flowNumber'], 'detail': r['detail'],
                        'heightRange': '2 a 8 in dentro de la abertura del ducto'}
    return r


def _duct_not_fit(v, c):
    return c.get('msg') or 'No se pudo calcular con estas medidas.'


# --------------------------------------------------------------------------
# Pleno
# --------------------------------------------------------------------------

def _plenum_fields(v):
    kind = v.get('kind') or 'horizSingle1N'
    opt = D.PLENUM_OPTIONS[kind]
    fields = [
        {'key': 'kind', 'type': 'select', 'label': 'Tipo de protección',
         'options': [{'value': k, 'label': o['label']} for k, o in D.PLENUM_OPTIONS.items()], 'default': kind,
         'reflow': True},
        {'key': 'lengthM', 'type': 'number', 'label': 'Largo del pleno (m)'},
    ]
    if 'maxWidthFt' in opt:
        max_width_m = E.fmt_num(E.ft_to_m(opt['maxWidthFt']))
        fields.append({'key': 'widthM', 'type': 'number', 'label': 'Ancho de pleno (m)',
                        'hint': f'Máximo permitido para esta variante: {max_width_m} m ({opt["maxWidthFt"]} ft).'})
    else:
        fields.append({'key': 'widthM', 'type': 'number', 'label': 'Ancho de pleno (m, opcional)', 'required': False,
                        'hint': 'Referencia informativa; esta variante no tiene un ancho máximo tabulado.'})
    fields.append({'key': 'qty', 'type': 'number', 'label': 'Cantidad de plenos idénticos', 'default': 1,
                    'hint': 'Las boquillas se multiplican por esta cantidad si hay más de un pleno igual en el sistema.'})
    return fields


def _plenum_required(v):
    kind = v.get('kind') or 'horizSingle1N'
    opt = D.PLENUM_OPTIONS[kind]
    req = ['lengthM']
    if 'maxWidthFt' in opt:
        req.append('widthM')
    return req


def _plenum_compute(v):
    kind = v.get('kind') or 'horizSingle1N'
    opt = D.PLENUM_OPTIONS[kind]
    length_m = _num(v.get('lengthM'))
    if not length_m:
        return {'ok': False}
    width_m = _num(v.get('widthM'))
    if 'maxWidthFt' in opt:
        if not width_m:
            return {'ok': False}
        max_width_m = E.ft_to_m(opt['maxWidthFt'])
        if width_m > max_width_m + 1e-9:
            return {'ok': False, 'widthExceeded': True, 'maxWidthM': max_width_m}
    length_ft = E.m_to_ft(length_m)
    qty = int(v.get('qty') or 1)
    result = E.calc_plenum(kind, length_ft, qty)
    # calc_plenum reporta la longitud en ft (unidad interna del motor); aquí
    # se re-expresa el detalle en metros, que es la unidad que capturó el
    # usuario.
    detail = f"{opt['label']} — {E.fmt_num(length_m)} m"
    if qty > 1:
        detail += f" — × {qty} plenos"
    result['detail'] = detail
    return {'ok': True, 'result': result}


def _plenum_not_fit(v, c):
    if c.get('widthExceeded'):
        return (f"El ancho capturado excede el máximo permitido de {E.fmt_num(c['maxWidthM'])} m para esta "
                'variante de pleno. Reduzca el ancho o elija otra variante de protección.')
    return 'Indique la longitud (y, si aplica, el ancho) del pleno en metros.'


# --------------------------------------------------------------------------
# Precipitador electrostático
# --------------------------------------------------------------------------

def _precipitator_fields(v):
    return [{'key': 'cells', 'type': 'number', 'label': 'Número de celdas', 'default': 1}]


def _precipitator_compute(v):
    return {'ok': True, 'result': E.calc_precipitator(v.get('cells') or 1)}


# ==========================================================================
# Tabla maestra
# ==========================================================================

CATEGORY_DEFS = {
    'fryer': {
        'has_choice': True, 'fields': _fryer_fields,
        'required_fields': lambda v: (['frypotD', 'frypotL', 'overallD', 'overallL'] if v.get('hasDripboard')
                                       else ['frypotD', 'frypotL']),
        'compute': _fryer_compute,
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: f"Altura de la boquilla sobre la tina: {m['hmin']} a {m['hmax']} in · Flow number: {m['flowPerNozzle']}",
        'result_from_choice': lambda c, i: E.fryer_result_for_choice(c, i),
        'not_fit_msg': _fryer_not_fit,
    },
    'tiltskillet': {
        'has_choice': True, 'fields': _tiltskillet_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': lambda v: E.calc_tilt_skillet(_num(v.get('d1')), _num(v.get('d2')), v.get('modules') or 1),
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: f"Altura de la boquilla sobre la superficie: {m['hmin']} a {m['hmax']} in · Flow number: {m['flowPerNozzle']}",
        'result_from_choice': lambda c, i: E.tilt_skillet_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: (f'Ninguna boquilla estándar cubre estas dimensiones, ni modularizando hasta '
                                      f'{E.MAX_AUTO_MODULES} zonas. Revise las medidas o consulte a ANSUL.'),
    },
    'range': {
        'has_choice': True, 'fields': _range_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': _range_compute,
        'choice_label': lambda m: f"Boquilla {m['nozzle']}" + (f" ×{m['qty']}" if m['qty'] > 1 else '') + f" — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · Lado máx {m['longSide']} in",
        'result_from_choice': lambda c, i: E.long_side_area_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna opción estándar cubre esta área, ni modularizando hasta '
                                      f'{E.MAX_AUTO_MODULES} zonas. Revise las medidas, o indique manualmente '
                                      'más módulos si sabe que necesitará más zonas.'),
    },
    'griddle': {
        'has_choice': True, 'fields': _griddle_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': lambda v: E.calc_long_side_area(D.GRIDDLE_OPTIONS, _num(v.get('d1')), _num(v.get('d2')), v.get('modules') or 1),
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · Lado máx {m['longSide']} in",
        'result_from_choice': lambda c, i: E.long_side_area_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna opción estándar cubre esta área, ni modularizando hasta '
                                      f'{E.MAX_AUTO_MODULES} zonas. Revise las medidas, o indique manualmente '
                                      'más módulos si sabe que necesitará más zonas.'),
    },
    'grill': {
        'has_choice': True, 'fields': _grill_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': _grill_compute,
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: (f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · "
                                  f"Lado máx {m['longSide']} in" + (f" · Profundidad máx {m['maxDepth']} in" if m.get('maxDepth') else '')),
        'result_from_choice': lambda c, i: E.grill_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna variante estándar de parrilla cubre estas dimensiones/combustible, '
                                      f'ni modularizando hasta {E.MAX_AUTO_MODULES} zonas. Revise las medidas o '
                                      'consulte a ANSUL.'),
    },
    'naturalcharcoal': {
        'has_choice': True, 'fields': _naturalcharcoal_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': lambda v: E.calc_grill('charcoal', _num(v.get('d1')), _num(v.get('d2')),
                                           _num(v.get('depth')) if v.get('depth') not in (None, '') else None,
                                           v.get('modules') or 1),
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: (f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · "
                                  f"Lado máx {m['longSide']} in" + (f" · Profundidad máx {m['maxDepth']} in" if m.get('maxDepth') else '')),
        'result_from_choice': lambda c, i: E.grill_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna variante estándar de asador de carbón cubre estas dimensiones, ni '
                                      f'modularizando hasta {E.MAX_AUTO_MODULES} zonas. Revise las medidas o '
                                      'consulte a ANSUL.'),
    },
    'woodgrill': {
        'has_choice': True, 'fields': _woodgrill_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': lambda v: E.calc_grill('wood', _num(v.get('d1')), _num(v.get('d2')),
                                           _num(v.get('depth')) if v.get('depth') not in (None, '') else None,
                                           v.get('modules') or 1),
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: (f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · "
                                  f"Lado máx {m['longSide']} in" + (f" · Profundidad máx {m['maxDepth']} in" if m.get('maxDepth') else '')),
        'result_from_choice': lambda c, i: E.grill_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna variante estándar de asador de leña cubre estas dimensiones, ni '
                                      f'modularizando hasta {E.MAX_AUTO_MODULES} zonas. Revise las medidas o '
                                      'consulte a ANSUL.'),
    },
    'robata': {
        'has_choice': True, 'fields': _robata_fields,
        'required_fields': lambda v: ['d1', 'd2'],
        'compute': _robata_compute,
        'choice_label': lambda m: f"Boquilla {m['nozzle']} — {m['tag']}{_module_suffix(m)}",
        'choice_sub': lambda m: (f"Altura: {m['hmin']} a {m['hmax']} in · Área máx {m['area']} in² · "
                                  f"Lado máx {m['longSide']} in" + (f" · Profundidad máx {m['maxDepth']} in" if m.get('maxDepth') else '')),
        'result_from_choice': lambda c, i: E.grill_result_for_choice(c, i),
        'not_fit_msg': lambda v, c: ('Ninguna variante estándar de robata (boquillas 1N/3N para combustible sólido) '
                                      f'cubre estas dimensiones, ni modularizando hasta {E.MAX_AUTO_MODULES} zonas. '
                                      'Revise las medidas o consulte a ANSUL.'),
    },
    'combioven': {
        'has_choice': False, 'fields': _combioven_fields,
        'required_fields': lambda v: [],
        'compute': _combioven_compute,
        'not_fit_msg': lambda v, c: '',
    },
    'kettle': {
        'has_choice': False, 'fields': _kettle_fields,
        'required_fields': lambda v: [],
        'compute': _kettle_compute,
        'not_fit_msg': lambda v, c: '',
    },
    'chainbroiler': {
        'has_choice': False, 'fields': _chainbroiler_fields,
        'required_fields': lambda v: ['length', 'width'],
        'compute': _chainbroiler_compute,
        'not_fit_msg': _chainbroiler_not_fit,
    },
    'uprightbroiler': {
        'has_choice': False, 'fields': _uprightbroiler_fields,
        'required_fields': lambda v: ['length', 'width'],
        'compute': lambda v: E.calc_upright_broiler(_num(v.get('length')), _num(v.get('width'))),
        'not_fit_msg': _uprightbroiler_not_fit,
    },
    'salamander': {
        'has_choice': True, 'fields': _salamander_fields,
        'required_fields': lambda v: ['length', 'width'],
        'compute': _salamander_compute,
        'choice_label': lambda m: m['label'],
        'choice_sub': lambda m: f"Superficie máx. protegida: {m['maxLength']} × {m['maxWidth']} in",
        'result_from_choice': lambda c, i: (E.salamander_result(c['matches'][i]) if 0 <= i < len(c['matches']) else None),
        'not_fit_msg': lambda v, c: 'Ninguna de las 3 opciones de salamandra cubre estas dimensiones.',
    },
    'wok': {
        'has_choice': True, 'fields': _wok_fields,
        'required_fields': lambda v: ['diam', 'depth'],
        'compute': _wok_compute,
        'choice_label': lambda m: f"Boquilla {m['nozzle']}",
        'choice_sub': lambda m: (f"Diámetro {m['diamMin']}-{m['diamMax']} in · Profundidad {m['depthMin']}-{m['depthMax']} in "
                                  f"· Altura de la boquilla sobre el wok: {m['hmin']}-{m['hmax']} in"),
        'result_from_choice': lambda c, i: (E.wok_result(c['matches'][i]) if 0 <= i < len(c['matches']) else None),
        'not_fit_msg': lambda v, c: 'Ningún wok estándar cubre este diámetro/profundidad.',
    },
    'duct': {
        'has_choice': False, 'fields': _duct_fields,
        'required_fields': _duct_required,
        'compute': _duct_compute,
        'not_fit_msg': _duct_not_fit,
    },
    'plenum': {
        'has_choice': False, 'fields': _plenum_fields,
        'required_fields': _plenum_required,
        'compute': _plenum_compute,
        'not_fit_msg': _plenum_not_fit,
    },
    'precipitator': {
        'has_choice': False, 'fields': _precipitator_fields,
        'required_fields': lambda v: [],
        'compute': _precipitator_compute,
        'not_fit_msg': lambda v, c: '',
    },
}


def has_required_inputs(category, values):
    """Replica hasRequiredInputs(def, f): todos los campos requeridos deben
    existir y ser números > 0."""
    cdef = CATEGORY_DEFS[category]
    req = cdef['required_fields'](values)
    for name in req:
        v = values.get(name)
        if v is None or v == '':
            return False
        try:
            n = float(v)
        except (TypeError, ValueError):
            return False
        if not (n > 0):
            return False
    return True


def category_display_label(item):
    if item.get('category') == 'range' and item.get('input', {}).get('burners'):
        b = item['input']['burners']
        return f'Estufa {b} Quemadores / Range {b} Burner'
    return D.CATEGORY_LABELS.get(item.get('category'), item.get('category'))


def _fmt_pair(largo, ancho, unit):
    """'{largo} x {ancho} {unit}', o solo el valor disponible si falta uno
    de los dos, o None si no hay ninguna medida capturada."""
    if largo is None and ancho is None:
        return None
    if largo is not None and ancho is not None:
        return f'{E.fmt_num(largo)} x {E.fmt_num(ancho)} {unit}'
    return f'{E.fmt_num(largo if largo is not None else ancho)} {unit}'


def dimensions_display(item):
    """Texto compacto 'Largo x Ancho' (o diámetro, para equipos redondos)
    con las medidas ya capturadas de un riesgo, para mostrar como columna
    en la tabla de "Riesgos, ductos y plenos". Devuelve None si la
    categoría no tiene medidas de footprint aplicables (Horno Combi,
    Precipitador) o si el usuario todavía no las ha capturado."""
    category = item.get('category')
    v = item.get('input') or {}

    def n(key):
        return _num(v.get(key))

    if category == 'fryer':
        if v.get('hasDripboard'):
            overall = _fmt_pair(n('overallD'), n('overallL'), 'in')
            if overall:
                return overall
        return _fmt_pair(n('frypotD'), n('frypotL'), 'in')

    if category in ('tiltskillet', 'range', 'griddle', 'grill', 'naturalcharcoal', 'woodgrill', 'robata'):
        # d2 = Largo (de frente a fondo), d1 = Ancho (de lado a lado)
        return _fmt_pair(n('d2'), n('d1'), 'in')

    if category in ('chainbroiler', 'uprightbroiler', 'salamander'):
        return _fmt_pair(n('length'), n('width'), 'in')

    if category == 'wok':
        d = n('diam')
        return f'Ø{E.fmt_num(d)} in' if d is not None else None

    if category == 'duct':
        if v.get('round'):
            d = n('diameter')
            return f'Ø{E.fmt_num(d)} in' if d is not None else None
        return _fmt_pair(n('sideA'), n('sideB'), 'in')  # Ancho x Alto del ducto

    if category == 'plenum':
        return _fmt_pair(n('lengthM'), n('widthM'), 'm')

    return None


def depth_display(item):
    """Medida de profundidad capturada aparte de "Largo x Ancho" — la
    profundidad del wok (obligatoria, parte del cálculo) o la profundidad
    opcional de la cama de brasas/carbón/leña en Parrilla, Asador de
    Carbón, Asador de Leña y Robata (de referencia/validación, no cambia
    el área). Devuelve None si la categoría no tiene esta medida o el
    usuario todavía no la ha capturado, para no mezclarla con "Largo x
    Ancho" — se muestra como su propio dato, por separado."""
    category = item.get('category')
    v = item.get('input') or {}

    def n(key):
        return _num(v.get(key))

    if category in ('wok', 'grill', 'naturalcharcoal', 'woodgrill', 'robata'):
        d = n('depth')
        return f'{E.fmt_num(d)} in' if d is not None else None

    return None
