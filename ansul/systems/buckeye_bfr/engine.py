# -*- coding: utf-8 -*-
"""
Motor de cálculo Buckeye Kitchen Mister (BFR-TM Rev. 6).

Convierte las medidas de cada riesgo en boquillas y flow points, y el total
de flow points de un sistema en combinaciones de cilindros BFR-5/10/15/20.
Las reglas y sus páginas están explicadas en docs/DISEÑO.md, sección 4.

Los resultados usan la misma forma que el motor ANSUL
({'nozzles', 'flowNumber', 'heightRange', 'detail'}) para que la interfaz y
el PDF los muestren igual; en Buckeye 'flowNumber' son FLOW POINTS.
"""
import math
from itertools import combinations_with_replacement

from . import data as D
from ...i18n import tr

EPS = 1e-9


def nozzle_flow(code):
    return D.nozzle_flow(code)


def _page(p):
    return tr('{0}, pág. {1}').format(D.MANUAL, p)


def _height_txt(opt):
    if opt.get('height'):
        return opt['height']
    return tr('{0} a {1} in').format(_fmt(opt['hmin']), _fmt(opt['hmax']))


def _fmt(n):
    if n is None:
        return '—'
    r = round(n * 100) / 100
    if r == int(r):
        return str(int(r))
    return f'{r:.2f}'.rstrip('0').rstrip('.')


# ----------------------------- Módulos (p. 3-11) ------------------------------

def module_grid(width, depth, cov_w, cov_d):
    """Menor cuadrícula de módulos IGUALES en la que cada módulo cabe en la
    cobertura de una boquilla (ancho ≤ cov_w y fondo ≤ cov_d).
    Regresa (columnas, filas)."""
    cols = max(1, math.ceil(width / cov_w - EPS))
    rows = max(1, math.ceil(depth / cov_d - EPS))
    return cols, rows


def _appliance_match(opt, width, depth):
    cols, rows = module_grid(width, depth, opt['w'], opt['d'])
    n = cols * rows
    flow = nozzle_flow(opt['nozzle'])
    m = dict(opt)
    m.update({'cols': cols, 'rows': rows, 'modulesCount': n, 'qty': n,
              'moduleW': width / cols, 'moduleD': depth / rows,
              'flowPerNozzle': flow, 'totalFlow': flow * n})
    return m


def calc_appliance(options, width, depth, max_modular_area=None, allow_modules=True):
    """Compara el área de cocción (ancho × fondo) contra cada opción de
    cobertura. Si no cabe en una sola boquilla, se divide en módulos iguales
    (p. 3-11). Regresa todas las opciones posibles, ordenadas por flow points
    totales, número de boquillas y altura máxima."""
    if not width or not depth or width <= 0 or depth <= 0:
        return {'ok': False, 'matches': []}
    area = width * depth
    matches = []
    blocked_by_area = False
    for opt in options:
        m = _appliance_match(opt, width, depth)
        if m['modulesCount'] > 1:
            if not allow_modules:
                continue
            if max_modular_area is not None and area > max_modular_area + EPS:
                blocked_by_area = True
                continue
        matches.append(m)
    matches.sort(key=lambda m: (m['totalFlow'], m['modulesCount'], -m.get('hmax', 0)))
    return {'ok': bool(matches), 'matches': matches, 'area': area,
            'overModularLimit': blocked_by_area and not matches}


def appliance_result(match, category_label=''):
    n = match['modulesCount']
    detail = match['tag']
    if n > 1:
        detail += (tr(' — {0} módulos iguales de {1} × {2} in ({3} × {4})').format(n, _fmt(match['moduleW']), _fmt(match['moduleD']), match['cols'], match['rows']))
    detail += tr('. Colocación: {0} ({1})').format(match['placement'], _page(match['page']))
    return {
        'nozzles': [{'code': match['nozzle'], 'qty': n}],
        'flowNumber': match['totalFlow'],
        'heightRange': _height_txt(match),
        'detail': detail,
    }


def range_options(back_shelf):
    if back_shelf:
        return [o for o in D.RANGE_OPTIONS if o['backShelf']]
    return [o for o in D.RANGE_OPTIONS if o['backShelf'] != 'only']


def calc_range(width, depth, back_shelf=False):
    return calc_appliance(range_options(back_shelf), width, depth)


def calc_range_griddle(width, depth):
    return calc_appliance(D.RANGE_GRIDDLE_OPTIONS, width, depth)


def calc_griddle(width, depth):
    return calc_appliance(D.GRIDDLE_OPTIONS, width, depth)


def calc_fryer(width, depth):
    return calc_appliance(D.FRYER_OPTIONS, width, depth, max_modular_area=D.FRYER_MAX_MODULAR_AREA)


def calc_tilt_skillet(width, depth):
    return calc_appliance(D.TILT_SKILLET_OPTIONS, width, depth)


def calc_charbroiler(kind, width, depth, fuel_depth=None):
    opt = D.CHARBROILER_OPTIONS.get(kind)
    if not opt:
        return {'ok': False, 'matches': []}
    if opt.get('maxFuelDepth') and fuel_depth is not None and fuel_depth > opt['maxFuelDepth'] + EPS:
        return {'ok': False, 'matches': [], 'fuelTooDeep': True, 'maxFuelDepth': opt['maxFuelDepth']}
    return calc_appliance([opt], width, depth)


def calc_upright_broiler(width, depth):
    """No se modulariza: una sola boquilla en la esquina superior (p. 3-10)."""
    return calc_appliance([D.UPRIGHT_BROILER], width, depth, allow_modules=False)


def calc_wok(diameter):
    w = D.WOK
    if diameter is None or diameter <= 0:
        return {'ok': False}
    if diameter < w['diamMin'] - EPS or diameter > w['diamMax'] + EPS:
        return {'ok': False, 'outOfRange': True}
    return {'ok': True, 'result': {
        'nozzles': [{'code': w['nozzle'], 'qty': 1}],
        'flowNumber': nozzle_flow(w['nozzle']),
        'heightRange': tr('{0} a {1} in (desde el fondo del wok)').format(w['hmin'], w['hmax']),
        'detail': tr('Wok de {0} in de diámetro. {1} ({2})').format(_fmt(diameter), w['placement'], _page(w['page'])),
    }}


# --------------------------------- Ductos -------------------------------------

def _rect_fits(opt, a, b):
    return 2 * (a + b) <= opt['maxPerimeter'] + EPS and max(a, b) <= opt['maxSide'] + EPS


def calc_duct(side_a=None, side_b=None, diameter=None, is_round=False):
    """Una boquilla si cabe; si un ducto rectangular pasa de 150 in de
    perímetro, varias N-2W en áreas iguales y simétricas (p. 3-2)."""
    if is_round:
        if not diameter or diameter <= 0:
            return {'ok': False}
        circ = math.pi * diameter
        for opt in D.DUCT_OPTIONS:
            if circ <= opt['maxCircumference'] + EPS and diameter <= opt['maxDiameter'] + EPS:
                return {'ok': True, 'nozzles': [{'code': opt['nozzle'], 'qty': 1}],
                        'flowNumber': nozzle_flow(opt['nozzle']),
                        'heightRange': opt['depth'],
                        'detail': (tr('Ducto redondo Ø{0} in (circunferencia {1} in) — {2} centrada, apuntando al centro del '
                                      'ducto ({3})').format(_fmt(diameter), _fmt(circ), opt['nozzle'], _page(opt['page'])))}
        return {'ok': False, 'needsManual': True,
                'msg': (tr('Ducto redondo de más de 150 in de circunferencia (47.5 in de diámetro): el manual no da '
                           'una protección estándar. Consulte al distribuidor Buckeye.'))}

    if not side_a or not side_b or side_a <= 0 or side_b <= 0:
        return {'ok': False}
    perimeter = 2 * (side_a + side_b)
    for opt in D.DUCT_OPTIONS:
        if _rect_fits(opt, side_a, side_b):
            return {'ok': True, 'nozzles': [{'code': opt['nozzle'], 'qty': 1}],
                    'flowNumber': nozzle_flow(opt['nozzle']),
                    'heightRange': opt['depth'],
                    'detail': (tr('Ducto {0} × {1} in (perímetro {2} in) — {3} centrada, apuntando al centro del ducto ({4})').format(_fmt(side_a), _fmt(side_b), _fmt(perimeter), opt['nozzle'], _page(opt['page'])))}

    big = D.DUCT_OPTIONS[-1]  # N-2W
    best = None
    for ca in range(1, D.DUCT_MAX_GRID + 1):
        for cb in range(1, D.DUCT_MAX_GRID + 1):
            if ca * cb < 2:
                continue
            if _rect_fits(big, side_a / ca, side_b / cb):
                key = (ca * cb, max(side_a / ca, side_b / cb))
                if best is None or key < best[0]:
                    best = (key, ca, cb)
    if not best:
        return {'ok': False, 'needsManual': True,
                'msg': tr('Ducto demasiado grande para dividirlo automáticamente. Consulte al distribuidor Buckeye.')}
    _, ca, cb = best
    n = ca * cb
    return {'ok': True, 'nozzles': [{'code': big['nozzle'], 'qty': n}],
            'flowNumber': nozzle_flow(big['nozzle']) * n,
            'heightRange': big['depth'],
            'detail': (tr('Ducto {0} × {1} in (perímetro {2} in > 150 in) — {3} boquillas N-2W, una al centro de '
                          'cada área igual de {4} × {5} in ({6} × {7}), apuntando dentro del ducto ({8})').format(_fmt(side_a), _fmt(side_b), _fmt(perimeter), n, _fmt(side_a / ca), _fmt(side_b / cb), ca, cb, _page('3-2')))}


def scale(result, qty, noun):
    qty = max(1, int(qty or 1))
    if not result or not result.get('ok') or qty == 1:
        return result
    out = dict(result)
    out['nozzles'] = [{'code': n['code'], 'qty': n['qty'] * qty} for n in result['nozzles']]
    out['flowNumber'] = result['flowNumber'] * qty
    out['detail'] = f"{result['detail']} — × {qty} {noun}"
    return out


# --------------------------------- Plenos -------------------------------------

def calc_plenum(kind, length_ft, width_ft=None):
    p = D.PLENUM
    k = D.PLENUM_KINDS.get(kind) or D.PLENUM_KINDS['single']
    if not length_ft or length_ft <= 0:
        return {'ok': False}
    if width_ft is not None and width_ft > p['maxWidthFt'] + EPS:
        return {'ok': False, 'widthExceeded': True}
    n = max(1, math.ceil(length_ft / p['maxLengthFt'] - EPS))
    zone = length_ft / n
    detail = tr('Pleno {0} — {1} boquilla{2} N-1HP').format(k['label'].lower(), n, 's' if n > 1 else '')
    if n > 1:
        detail += tr(', tramos iguales de {0} ft').format(_fmt(zone))
    detail += tr('. Colocación: {0} ({1})').format(k['placement'], _page(p['page']))
    return {'ok': True, 'nozzles': [{'code': p['nozzle'], 'qty': n}],
            'flowNumber': nozzle_flow(p['nozzle']) * n, 'heightRange': tr('1/3 de la altura (ver detalle)'),
            'detail': detail}


# ------------------------------ Cilindros -------------------------------------

def nozzle_counts(nozzle_totals):
    """(n1, n2): cuántas boquillas de 1 y de 2 flow points hay."""
    n1 = sum(q for c, q in nozzle_totals.items() if nozzle_flow(c) == 1)
    n2 = sum(q for c, q in nozzle_totals.items() if nozzle_flow(c) == 2)
    return n1, n2


def combo_fits(capacities, n1, n2):
    """¿Las boquillas caben en estos cilindros? Una boquilla de 2 FP no se puede
    repartir entre dos cilindros (ver DISEÑO.md 4.3)."""
    return n2 <= sum(c // 2 for c in capacities) and n1 + 2 * n2 <= sum(capacities)


def cylinder_combinations(n1, n2, sizes=D.CYLINDER_SIZES, max_total=300):
    """Todas las combinaciones mínimas de cilindros: alcanzan para las
    boquillas y, si se quita cualquier cilindro, ya no alcanzan. Ordenadas
    por sobrante de flow points y luego por número de cilindros."""
    total = n1 + 2 * n2
    if total <= 0:
        return []
    if total > max_total:
        return None
    max_count = math.ceil(total / 4) + 1
    out = []
    for count in range(1, max_count + 1):
        for combo in combinations_with_replacement(sorted(sizes, reverse=True), count):
            if not combo_fits(combo, n1, n2):
                continue
            minimal = True
            for i in range(len(combo)):
                rest = combo[:i] + combo[i + 1:]
                if rest and combo_fits(rest, n1, n2):
                    minimal = False
                    break
            if minimal:
                cap = sum(combo)
                out.append({'cylinders': list(combo), 'capacity': cap, 'surplus': cap - total,
                            'count': len(combo)})
    out.sort(key=lambda c: (c['surplus'], c['count'], [-x for x in c['cylinders']]))
    return out


def combo_label(cylinders):
    counts = {}
    for c in cylinders:
        counts[c] = counts.get(c, 0) + 1
    return ' + '.join(f"{n} × {D.CYLINDERS[s]['model']}" for s, n in sorted(counts.items(), reverse=True))


# ------------------------------ Resúmenes -------------------------------------

def kitchen_summary(kitchen):
    nozzle_totals = {}
    total_flow = 0
    rows = []
    categories = set()
    for item in kitchen.get('equipment', []):
        r = item.get('result')
        if not r:
            continue
        categories.add(item.get('category'))
        total_flow += r.get('flowNumber') or 0
        for n in r.get('nozzles') or []:
            nozzle_totals[n['code']] = nozzle_totals.get(n['code'], 0) + n['qty']
        rows.append(item)

    n1, n2 = nozzle_counts(nozzle_totals)
    combos = cylinder_combinations(n1, n2)
    notes = []
    chosen = None
    if combos is None:
        notes.append(tr('El sistema excede 300 flow points: divídalo en varios sistemas.'))
        combos = []
    saved = kitchen.get('cylinderChoice')
    if combos:
        if saved:
            chosen = next((c for c in combos if sorted(c['cylinders']) == sorted(saved)), None)
            if chosen is None:
                notes.append(tr('La combinación de cilindros guardada ({0}) ya no es válida con los riesgos actuales; se '
                                'usa la primera opción de la lista. Elija otra si lo desea.').format(combo_label(saved)))
        if chosen is None:
            chosen = combos[0]

    needs_min = bool(categories & set(D.MIN_PIPING_CATEGORIES))
    if needs_min and 0 < total_flow < D.MIN_SYSTEM_FLOW_POINTS:
        notes.append(tr('ADVERTENCIA: el sistema tiene {0} flow point(s); el mínimo es {1} (p. 3-13).').format(total_flow, D.MIN_SYSTEM_FLOW_POINTS))
    if needs_min and total_flow > 0:
        notes.append(tr('Requisitos mínimos de tubería (protege wok, freidora o estufa, p. 3-13): ')
                     + ' '.join(D.MIN_PIPING_NOTES[:3]))

    cyl_counts = {}
    if chosen:
        for c in chosen['cylinders']:
            cyl_counts[c] = cyl_counts.get(c, 0) + 1

    return {'totalFlow': total_flow, 'nozzleTotals': nozzle_totals, 'itemCount': len(kitchen.get('equipment', [])),
            'rows': rows, 'combos': combos, 'chosen': chosen, 'cylinderCounts': cyl_counts,
            'notes': notes, 'n1': n1, 'n2': n2}


def project_summary(project):
    nozzle_totals = {}
    cyl_counts = {}
    total_flow = 0
    kitchen_summaries = []
    for k in project.get('kitchens', []):
        s = kitchen_summary(k)
        kitchen_summaries.append({'kitchen': k, 'summary': s})
        for code, qty in s['nozzleTotals'].items():
            nozzle_totals[code] = nozzle_totals.get(code, 0) + qty
        for size, qty in s['cylinderCounts'].items():
            cyl_counts[size] = cyl_counts.get(size, 0) + qty
        total_flow += s['totalFlow']
    return {'nozzleTotals': nozzle_totals, 'cylinderCounts': cyl_counts, 'totalFlow': total_flow,
            'totalCylinders': sum(cyl_counts.values()), 'kitchenSummaries': kitchen_summaries}
