# -*- coding: utf-8 -*-
"""
Campos de captura y cálculo por categoría — Buckeye Kitchen Mister.
Mismo formato que ansul/category_defs.py (ver la explicación de cada llave
en ese archivo), para que el formulario dinámico de la interfaz funcione
igual con las dos marcas.
"""
from . import data as D
from . import engine as E
from ...i18n import tr


def _num(v):
    if v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


_W = {'key': 'width', 'type': 'number', 'label': tr('Ancho del área de cocción (in)'),
      'hint': tr('De lado a lado. Es el área que se usa para cocinar, no el tamaño exterior del equipo (p. '
                 '3-3).')}
_D = {'key': 'depth', 'type': 'number', 'label': tr('Fondo del área de cocción (in)'),
      'hint': tr('De frente a atrás.')}
_W_BURNERS = dict(_W, hint=tr('De lado a lado, medido de borde a borde de los quemadores (p. 3-3).'))
_D_BURNERS = dict(_D, hint=tr('De frente a atrás, de borde a borde de los quemadores.'))


def _wd(v):
    return _num(v.get('width')), _num(v.get('depth'))


def _choice_label(m):
    n = m['modulesCount']
    qty = f" ×{n}" if n > 1 else ''
    mods = tr(' · {0} módulos ({1} × {2})').format(n, m['cols'], m['rows']) if n > 1 else ''
    return tr('Boquilla {0}{1} — {2}{3}').format(m['nozzle'], qty, m['tag'], mods)


def _choice_sub(m):
    h = m.get('height') or tr('{0} a {1} in').format(E._fmt(m['hmin']), E._fmt(m['hmax']))
    return (tr('Altura: {0} · Cobertura por boquilla: {1} × {2} in · Flow points: {3} · pág. {4}').format(h, E._fmt(m['w']), E._fmt(m['d']), m['totalFlow'], m['page']))


def _result(c, i):
    matches = c.get('matches') or []
    if i is None or not (0 <= i < len(matches)):
        return None
    return E.appliance_result(matches[i])


def _no_fit(v, c):
    if c.get('overModularLimit'):
        return (tr('El área ({0} in²) es mayor a {1} in²: es el tamaño máximo de freidora que se puede '
                   'modularizar (p. 3-7 / 3-11). Divídala en riesgos independientes.').format(E._fmt(c['area']), D.FRYER_MAX_MODULAR_AREA))
    return tr('Ninguna cobertura del manual Buckeye cubre estas medidas. Revise las medidas o consulte '
              'al distribuidor.')


def _appliance_def(fields, compute):
    return {'has_choice': True, 'fields': fields, 'required_fields': lambda v: ['width', 'depth'],
            'compute': compute, 'choice_label': _choice_label, 'choice_sub': _choice_sub,
            'result_from_choice': _result, 'not_fit_msg': _no_fit}


# ---- Estufa ------------------------------------------------------------------

def _range_fields(v):
    return [
        {'key': 'backShelf', 'type': 'toggle', 'label': tr('¿Tiene repisa trasera (back-shelf)?'), 'default': False,
         'hint': tr('Con repisa solo se ofrecen las coberturas que la tabla p. 3-12 marca para repisa.')},
        dict(_W_BURNERS), dict(_D_BURNERS),
    ]


def _range_compute(v):
    w, d = _wd(v)
    return E.calc_range(w, d, bool(v.get('backShelf')))


# ---- Asador (charbroiler) ---------------------------------------------------

def _charbroiler_fields(v):
    kind = v.get('kind') or 'radiant'
    fields = [
        {'key': 'kind', 'type': 'select', 'label': tr('Tipo de asador'),
         'options': [{'value': k, 'label': lbl} for k, lbl in D.CHARBROILER_TYPE_LABELS.items()],
         'default': 'radiant', 'reflow': True},
        dict(_W), dict(_D),
    ]
    if kind == 'solid':
        fields.append({'key': 'fuelDepth', 'type': 'number', 'label': tr('Profundidad del combustible (in, opcional)'),
                       'required': False, 'hint': tr('Máximo 6 in (p. 3-11).')})
    return fields


def _charbroiler_compute(v):
    w, d = _wd(v)
    kind = v.get('kind') or 'radiant'
    fd = _num(v.get('fuelDepth')) if kind == 'solid' else None
    return E.calc_charbroiler(kind, w, d, fd)


def _charbroiler_no_fit(v, c):
    if c.get('fuelTooDeep'):
        return tr('La profundidad del combustible excede el máximo de {0} in (p. 3-11).').format(c['maxFuelDepth'])
    return _no_fit(v, c)


# ---- Wok ---------------------------------------------------------------------

def _wok_fields(v):
    return [{'key': 'diam', 'type': 'number', 'label': tr('Diámetro del wok (in)'),
             'hint': tr('Cobertura: {0} in mínimo a {1} in máximo (p. 3-6).').format(D.WOK['diamMin'], D.WOK['diamMax'])}]


def _wok_no_fit(v, c):
    return (tr('El manual Buckeye cubre woks de {0} a {1} in de diámetro (p. 3-6). Consulte al '
               'distribuidor.').format(D.WOK['diamMin'], D.WOK['diamMax']))


# ---- Ducto -------------------------------------------------------------------

def _duct_fields(v, with_qty_label=tr('Cantidad de ductos idénticos')):
    fields = [{'key': 'round', 'type': 'toggle', 'label': tr('Ducto redondo'), 'default': False, 'reflow': True}]
    if v.get('round'):
        fields.append({'key': 'diameter', 'type': 'number', 'label': tr('Diámetro (in)')})
    else:
        fields += [
            {'key': 'sideA', 'type': 'number', 'label': tr('Ancho del ducto (in)')},
            {'key': 'sideB', 'type': 'number', 'label': tr('Alto / fondo del ducto (in)')},
        ]
    fields.append({'key': 'qty', 'type': 'number', 'label': with_qty_label, 'default': 1, 'required': False,
                   'hint': tr('En campanas con varios collarines (pleno superior/inferior) cada uno se protege como un '
                              'ducto individual (p. 3-2).')})
    return fields


def _duct_required(v):
    return ['diameter'] if v.get('round') else ['sideA', 'sideB']


def _duct_base(v):
    if v.get('round'):
        return E.calc_duct(diameter=_num(v.get('diameter')), is_round=True)
    return E.calc_duct(_num(v.get('sideA')), _num(v.get('sideB')))


def _as_result(r):
    if r.get('ok'):
        r = dict(r)
        r['result'] = {k: r[k] for k in ('nozzles', 'flowNumber', 'heightRange', 'detail')}
    return r


def _duct_compute(v):
    return _as_result(E.scale(_duct_base(v), v.get('qty') or 1, 'ductos'))


def _precipitator_fields(v):
    return ([{'key': '_info', 'type': 'info',
              'label': tr('Los precipitadores electrostáticos llevan protección de ducto arriba y abajo del '
                          'precipitador, con boquillas estándar de ducto (p. 3-2). Capture las medidas del ducto.')}]
            + _duct_fields(v, tr('Cantidad de precipitadores idénticos')))


def _precipitator_compute(v):
    base = _duct_base(v)
    if not base.get('ok'):
        return base
    two = E.scale(base, 2, tr('boquillas: arriba y abajo del precipitador'))
    two = dict(two)
    two['detail'] = tr('Precipitador: protección arriba y abajo (p. 3-2). {0}').format(base['detail'])
    return _as_result(E.scale(two, v.get('qty') or 1, 'precipitadores'))


def _duct_no_fit(v, c):
    return c.get('msg') or tr('Capture las medidas del ducto.')


# ---- Pleno -------------------------------------------------------------------

M_TO_FT = 1 / 0.3048


def _plenum_fields(v):
    return [
        {'key': 'kind', 'type': 'select', 'label': tr('Tipo de pleno'),
         'options': [{'value': k, 'label': o['label']} for k, o in D.PLENUM_KINDS.items()], 'default': 'single'},
        {'key': 'lengthM', 'type': 'number', 'label': tr('Largo del pleno (m)'),
         'hint': tr('Una boquilla N-1HP por cada tramo de 12 ft (3.7 m); se reparten en tramos iguales (p. '
                    '3-3).')},
        {'key': 'widthM', 'type': 'number', 'label': tr('Ancho del pleno (m)'),
         'hint': tr('Máximo 4 ft (1.22 m) por boquilla (p. 3-3).')},
        {'key': 'qty', 'type': 'number', 'label': tr('Cantidad de plenos idénticos'), 'default': 1, 'required': False},
    ]


def _plenum_compute(v):
    lm, wm = _num(v.get('lengthM')), _num(v.get('widthM'))
    r = E.calc_plenum(v.get('kind') or 'single', lm * M_TO_FT if lm else None, wm * M_TO_FT if wm else None)
    if r.get('ok'):
        r['detail'] = f"{E._fmt(lm)} m — " + r['detail']
    return _as_result(E.scale(r, v.get('qty') or 1, 'plenos'))


def _plenum_no_fit(v, c):
    if c.get('widthExceeded'):
        return tr('El ancho excede el máximo de 4 ft (1.22 m) por boquilla (p. 3-3). Consulte al '
                  'distribuidor.')
    return tr('Indique el largo y el ancho del pleno en metros.')


# ==========================================================================

CATEGORY_DEFS = {
    'fryer': _appliance_def(lambda v: [dict(_W, label=tr('Ancho de la tina / área de cocción (in)')),
                                       dict(_D, label=tr('Fondo de la tina / área de cocción (in)'))],
                            lambda v: E.calc_fryer(*_wd(v))),
    'tiltskillet': _appliance_def(lambda v: [dict(_W), dict(_D)], lambda v: E.calc_tilt_skillet(*_wd(v))),
    'range': _appliance_def(_range_fields, _range_compute),
    'rangegriddle': _appliance_def(lambda v: [dict(_W_BURNERS), dict(_D_BURNERS)],
                                   lambda v: E.calc_range_griddle(*_wd(v))),
    'griddle': _appliance_def(lambda v: [dict(_W), dict(_D)], lambda v: E.calc_griddle(*_wd(v))),
    'charbroiler': dict(_appliance_def(_charbroiler_fields, _charbroiler_compute), not_fit_msg=_charbroiler_no_fit),
    'uprightbroiler': _appliance_def(
        lambda v: [dict(_W, label=tr('Ancho de la parrilla de cocción (in)')),
                   dict(_D, label=tr('Fondo de la parrilla de cocción (in)'))],
        lambda v: E.calc_upright_broiler(*_wd(v))),
    'wok': {'has_choice': False, 'fields': _wok_fields, 'required_fields': lambda v: ['diam'],
            'compute': lambda v: E.calc_wok(_num(v.get('diam'))), 'not_fit_msg': _wok_no_fit},
    'duct': {'has_choice': False, 'fields': _duct_fields, 'required_fields': _duct_required,
             'compute': _duct_compute, 'not_fit_msg': _duct_no_fit},
    'plenum': {'has_choice': False, 'fields': _plenum_fields, 'required_fields': lambda v: ['lengthM', 'widthM'],
               'compute': _plenum_compute, 'not_fit_msg': _plenum_no_fit},
    'precipitator': {'has_choice': False, 'fields': _precipitator_fields, 'required_fields': _duct_required,
                     'compute': _precipitator_compute, 'not_fit_msg': _duct_no_fit},
}
assert set(CATEGORY_DEFS) == set(D.CATEGORY_ORDER)


def has_required_inputs(category, values):
    req = CATEGORY_DEFS[category]['required_fields'](values)
    for name in req:
        n = _num(values.get(name))
        if n is None or not n > 0:
            return False
    return True


def category_display_label(item):
    return D.CATEGORY_LABELS.get(item.get('category'), item.get('category'))


def dimensions_display(item):
    c = item.get('category')
    v = item.get('input') or {}
    if c in ('duct', 'precipitator'):
        if v.get('round'):
            d = _num(v.get('diameter'))
            return tr('Ø{0} in').format(E._fmt(d)) if d else None
        a, b = _num(v.get('sideA')), _num(v.get('sideB'))
        return tr('{0} x {1} in').format(E._fmt(a), E._fmt(b)) if a and b else None
    if c == 'wok':
        d = _num(v.get('diam'))
        return tr('Ø{0} in').format(E._fmt(d)) if d else None
    if c == 'plenum':
        lm, wm = _num(v.get('lengthM')), _num(v.get('widthM'))
        return f'{E._fmt(lm)} x {E._fmt(wm)} m' if lm and wm else None
    w, d = _num(v.get('width')), _num(v.get('depth'))
    # Mismo orden que ANSUL en la tabla: "Largo (fondo) x Ancho"
    return tr('{0} x {1} in').format(E._fmt(d), E._fmt(w)) if w and d else None


def depth_display(item):
    if item.get('category') == 'charbroiler':
        d = _num((item.get('input') or {}).get('fuelDepth'))
        return tr('{0} in').format(E._fmt(d)) if d else None
    return None


def diagram_spec(category, values):
    """('rect', ancho, fondo, unidad) | ('circle', diámetro, unidad) | None"""
    if category == 'wok':
        d = _num(values.get('diam'))
        return ('circle', d, 'in') if d and d > 0 else None
    if category in ('duct', 'precipitator'):
        if values.get('round'):
            d = _num(values.get('diameter'))
            return ('circle', d, 'in') if d and d > 0 else None
        a, b = _num(values.get('sideA')), _num(values.get('sideB'))
        return ('rect', a, b, 'in') if a and b and a > 0 and b > 0 else None
    if category == 'plenum':
        lm, wm = _num(values.get('lengthM')), _num(values.get('widthM'))
        return ('rect', wm, lm, 'm') if lm and wm and lm > 0 and wm > 0 else None
    w, d = _num(values.get('width')), _num(values.get('depth'))
    return ('rect', w, d, 'in') if w and d and w > 0 and d > 0 else None
