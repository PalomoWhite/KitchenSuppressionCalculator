# -*- coding: utf-8 -*-
"""
Motor de cálculo — traduce las medidas de un equipo/riesgo de cocina en
boquillas / "flow number" y, a nivel sistema/proyecto, en tanques y
cartuchos requeridos.

Puerto directo (1:1) de la lógica ya validada en AnsulCalc.html. Cada
función conserva el mismo nombre y comportamiento que su contraparte en
JavaScript para poder auditar el código contra el manual ANSUL(R) R-102
línea por línea si hace falta.
"""
import math

from . import data as D
from .model_catalog import MODEL_CATALOG

# --------------------------- Utilidades numéricas --------------------------


def num(v):
    """Replica num(f.x): castea a float; None/'' -> None."""
    if v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt_num(n):
    if n is None:
        return '—'
    try:
        if math.isnan(n):
            return '—'
    except TypeError:
        return '—'
    r = round(n * 100) / 100
    if r == int(r):
        return str(int(r))
    s = f'{r:.2f}'.rstrip('0').rstrip('.')
    return s


def nozzle_flow(code):
    return D.nozzle_flow(code)


# --------------------------- Conversión de unidades -------------------------
# 1 metro = 3.28084 ft; 1 in = 2.54 cm (valores usados también por el
# convertidor de unidades del menú Herramientas y por el convertidor rápido
# integrado en "Agregar riesgo").
FT_TO_M = 0.3048
M_TO_FT = 1 / FT_TO_M
IN_TO_CM = 2.54
CM_TO_IN = 1 / IN_TO_CM


def ft_to_m(ft):
    return None if ft is None else ft * FT_TO_M


def in_to_cm(inches):
    return None if inches is None else inches * IN_TO_CM


def cm_to_in(cm):
    return None if cm is None else cm * CM_TO_IN


def m_to_ft(m):
    return None if m is None else m * M_TO_FT


def fits_box(d1, d2, max_a, max_b):
    """¿La caja (d1 x d2) cabe dentro de (max_a x max_b) en alguna orientación?"""
    return (d1 <= max_a and d2 <= max_b) or (d1 <= max_b and d2 <= max_a)


def fits_long_side_area(d1, d2, long_side_max, area_max):
    long_side = max(d1, d2)
    area = d1 * d2
    return long_side <= long_side_max + 1e-9 and area <= area_max + 1e-9


def scale_result_by_qty(base, qty, noun):
    if not base or not base.get('ok') or qty <= 1:
        return base
    nozzles = [{'code': n['code'], 'qty': n['qty'] * qty} for n in base['nozzles']]
    flow_number = base['flowNumber'] * qty
    out = dict(base)
    out['nozzles'] = nozzles
    out['flowNumber'] = flow_number
    out['qty'] = qty
    out['detail'] = f"{base['detail']} — × {qty} {noun}s"
    return out


def catalog_flow_number(nozzles):
    return sum(nozzle_flow(n['code']) * n['qty'] for n in (nozzles or []))


def _duct_res(nozzles, detail):
    flow_number = sum(nozzle_flow(n['code']) * n['qty'] for n in nozzles)
    return {'ok': True, 'nozzles': nozzles, 'flowNumber': flow_number, 'detail': detail}


# --------------------------- Modularización automática ----------------------
# Método general de modularización de equipos sobredimensionados, tomado del
# manual R-102 (Sección 4, "Fryer – Multiple Nozzle Protection", pág. 4-10 a
# 4-12): un equipo más grande de lo que cubre una sola boquilla se divide en
# N zonas iguales a lo largo de su lado más largo; cada zona debe caber
# dentro del área/lado máximo de una boquilla estándar. El mismo método se
# generaliza aquí a Estufa, Plancha, Parrilla/Robata (tabla "lado más largo +
# área") y a Sartén de Volteo (tabla de cajas de Freidora, por instrucción
# explícita del manual en la pág. 4-12). Si el usuario no indica cuántos
# módulos quiere (o dejó el valor por defecto, 1), el programa calcula
# automáticamente el mínimo necesario; si el usuario pide más módulos de los
# estrictamente necesarios, se respeta ese mínimo solicitado.
MAX_AUTO_MODULES = 8


def _modularize_long_side_area(options, d1, d2, modules=None, max_modules=MAX_AUTO_MODULES):
    """Divide la dimensión más larga del equipo (d1/d2) entre N zonas
    iguales y busca, para el N más pequeño posible (a partir de lo pedido
    por el usuario), qué opciones de la tabla 'options' caben en una zona.
    Regresa (n, matches) — matches ya trae 'modulesCount': n en cada
    renglón para que la interfaz pueda mostrar el total de zonas."""
    long_side = max(d1, d2)
    short_side = min(d1, d2)

    def matches_for(n):
        seg = long_side / n
        out = [dict(opt, modulesCount=n) for opt in options
               if fits_long_side_area(seg, short_side, opt['longSide'], opt['area'])]
        out.sort(key=lambda m: (m['qty'] * nozzle_flow(m['nozzle']), m['hmax']))
        return out

    n = max(int(modules or 1), 1)
    matches = matches_for(n)
    while not matches and n < max_modules:
        n += 1
        matches = matches_for(n)
    return n, matches


def _dedupe_nozzle_matches(matches):
    """Varios de los 'grupos' de D.FRYER_GROUPS representan cajas que se
    solapan entre sí a propósito (p.ej. una tina de 14x15 in también cabe
    dentro de la caja más grande de 19.5x19 in de otro grupo) — el manual
    documenta ambas filas de la tabla por separado porque corresponden a
    tinas de tamaño distinto, pero cuando una medida capturada satisface
    más de un grupo a la vez, esas filas pueden coincidir exactamente en
    boquilla y rango de altura. Sin este filtro, la lista de opciones le
    mostraría al usuario la misma boquilla al mismo rango de altura
    repetida más de una vez. Se conserva solo la primera aparición de
    cada combinación (boquilla, altura mínima, altura máxima, módulos) —
    el orden de la lista (ya ordenada por flow/altura) no cambia."""
    seen = set()
    out = []
    for m in matches:
        key = (m['nozzle'], m['hmin'], m['hmax'], m.get('modulesCount', 1))
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    return out


def _modularize_box(groups, d1, d2, modules=None, max_modules=MAX_AUTO_MODULES):
    """Variante del método anterior para categorías que usan cajas
    (ancho x fondo) en vez de lado más largo + área — Sartén de Volteo,
    reutilizando D.FRYER_GROUPS y su caja 'overall' (máximo con
    escurridor), tal como indica el manual para tilt skillets/braising
    pans (pág. 4-12)."""
    long_side = max(d1, d2)
    short_side = min(d1, d2)

    def matches_for(n):
        seg = long_side / n
        out = []
        for g in groups:
            if not fits_box(seg, short_side, g['overall'][0], g['overall'][1]):
                continue
            for opt in g['opts']:
                out.append({'group': g['id'], 'nozzle': opt['nozzle'], 'tag': opt['tag'],
                            'hmin': opt['hmin'], 'hmax': opt['hmax'],
                            'flowPerNozzle': nozzle_flow(opt['nozzle']), 'modulesCount': n})
        out.sort(key=lambda m: (m['flowPerNozzle'], m['hmax']))
        return _dedupe_nozzle_matches(out)

    n = max(int(modules or 1), 1)
    matches = matches_for(n)
    while not matches and n < max_modules:
        n += 1
        matches = matches_for(n)
    return n, matches


# ------------------------------ Freidoras -----------------------------------

def calc_fryer(hasDripboard, frypotD, frypotL, overallD, overallL, modules, fuel='gas'):
    fd, fl = frypotD, frypotL
    od = overallD if hasDripboard else fd
    ol = overallL if hasDripboard else fl
    total_area = od * ol if hasDripboard else fd * fl
    over_limit = total_area > D.FRYER_MAX_TOTAL_AREA  # tope absoluto: no aplica dividir por módulos (pág. 4-10)

    def matches_for(n):
        out = []
        for g in D.FRYER_GROUPS:
            if g.get('electric') and fuel != 'electric':
                continue  # grupo G: solo freidora eléctrica vat dividida
            if n > 1:
                # Modularizando (2+ zonas): se permite usar el tamaño "con
                # escurridor" de cada grupo para cada zona, sin importar si
                # el equipo tiene escurridor o no (pág. 4-10).
                long_side = max(od, ol) / n
                short_side = min(od, ol)
                fits = fits_box(long_side, short_side, g['overall'][0], g['overall'][1])
            else:
                fits = fits_box(fd, fl, g['frypot'][0], g['frypot'][1])
                if fits and hasDripboard:
                    fits = fits_box(od, ol, g['overall'][0], g['overall'][1])
            if not fits:
                continue
            for opt in g['opts']:
                out.append({'group': g['id'], 'nozzle': opt['nozzle'], 'tag': opt['tag'],
                            'hmin': opt['hmin'], 'hmax': opt['hmax'],
                            'flowPerNozzle': nozzle_flow(opt['nozzle']), 'modulesCount': n})
        out.sort(key=lambda m: (m['flowPerNozzle'], m['hmax']))
        return _dedupe_nozzle_matches(out)

    n = max(int(modules or 1), 1)
    matches = matches_for(n)
    while not matches and not over_limit and n < MAX_AUTO_MODULES:
        n += 1
        matches = matches_for(n)

    return {
        'ok': len(matches) > 0 and not over_limit,
        'matches': matches, 'modules': n, 'totalArea': total_area, 'overLimit': over_limit,
        'needsModularization': len(matches) == 0,
    }


def fryer_result_for_choice(fryer_calc, chosen_index):
    matches = fryer_calc['matches']
    if chosen_index is None or chosen_index < 0 or chosen_index >= len(matches):
        return None
    m = matches[chosen_index]
    qty = m.get('modulesCount', fryer_calc['modules'])
    detail = f"{m['tag']} — grupo {m['group']}"
    if qty > 1:
        detail += f" — modularizado en {qty} zonas"
    return {
        'nozzles': [{'code': m['nozzle'], 'qty': qty}],
        'flowNumber': m['flowPerNozzle'] * qty,
        'heightRange': f"{m['hmin']} in a {m['hmax']} in",
        'detail': detail,
    }


# ---------------------------- Sartén de volteo -------------------------------

def calc_tilt_skillet(d1, d2, modules=None):
    non_electric_groups = [g for g in D.FRYER_GROUPS if not g.get('electric')]
    n, matches = _modularize_box(non_electric_groups, d1, d2, modules)
    return {'ok': len(matches) > 0, 'matches': matches, 'modules': n}


def tilt_skillet_result_for_choice(c, chosen_index):
    return fryer_result_for_choice(c, chosen_index)


# -------------------- Estufa / Plancha (lado más largo + área) --------------

def calc_long_side_area(options, d1, d2, modules=None):
    n, matches = _modularize_long_side_area(options, d1, d2, modules)
    return {'ok': len(matches) > 0, 'matches': matches, 'modules': n}


def long_side_area_result_for_choice(calc, chosen_idx):
    """chosen_idx es la POSICIÓN del renglón elegido dentro de calc['matches']
    (la lista ya filtrada y ordenada que se le mostró al usuario) — no el
    índice original dentro de la tabla de opciones."""
    matches = calc['matches']
    if chosen_idx is None or not (0 <= chosen_idx < len(matches)):
        return None
    m = matches[chosen_idx]
    n = m.get('modulesCount', calc['modules'])
    total_qty = m['qty'] * n
    detail = m['tag']
    if n > 1:
        detail += f" — modularizado en {n} zonas"
    return {
        'nozzles': [{'code': m['nozzle'], 'qty': total_qty}],
        'flowNumber': nozzle_flow(m['nozzle']) * total_qty,
        'heightRange': f"{m['hmin']} in a {m['hmax']} in",
        'detail': detail,
    }


# --------------------------------- Parrillas ---------------------------------

def calc_grill(fuel, d1, d2, depth, modules=None):
    def depth_ok(v):
        max_depth = v.get('maxDepth')
        return not (max_depth and depth is not None and depth > max_depth)

    eligible = [v for v in D.GRILL_VARIANTS if fuel in v['fuels'] and depth_ok(v)]
    n, matches = _modularize_long_side_area(eligible, d1, d2, modules)
    return {'ok': len(matches) > 0, 'matches': matches, 'fuel': fuel, 'modules': n}


# Robata: reutiliza específicamente las dos variantes de combustible sólido
# ya validadas de GRILL_VARIANTS (naturalCharcoal -> 1N, woodFueled -> 3N),
# NUNCA la variante mixta 'lavaOrCharcoalAlt' (esa es para Parrilla/Grill con
# cama de lava que opcionalmente admite carbón, un equipo distinto).
ROBATA_VARIANT_KEYS = {'charcoal': 'naturalCharcoal', 'wood': 'woodFueled'}


def calc_robata(fuel, d1, d2, depth, modules=None):
    variant = next((v for v in D.GRILL_VARIANTS if v['key'] == ROBATA_VARIANT_KEYS.get(fuel)), None)
    eligible = [variant] if variant else []
    max_depth = variant.get('maxDepth') if variant else None
    if max_depth and depth is not None and depth > max_depth:
        eligible = []
    n, matches = _modularize_long_side_area(eligible, d1, d2, modules)
    return {'ok': len(matches) > 0, 'matches': matches, 'fuel': fuel, 'modules': n}


def grill_result_for_choice(calc, chosen_idx):
    """chosen_idx es la POSICIÓN del renglón elegido dentro de calc['matches']."""
    matches = calc['matches']
    if chosen_idx is None or not (0 <= chosen_idx < len(matches)):
        return None
    m = matches[chosen_idx]
    n = m.get('modulesCount', calc['modules'])
    total_qty = m['qty'] * n
    detail = f"{m['tag']} ({D.FUEL_LABELS.get(calc['fuel'], calc['fuel'])})"
    if n > 1:
        detail += f" — modularizado en {n} zonas"
    return {
        'nozzles': [{'code': m['nozzle'], 'qty': total_qty}],
        'flowNumber': nozzle_flow(m['nozzle']) * total_qty,
        'heightRange': f"{m['hmin']} in a {m['hmax']} in",
        'detail': detail,
    }


# ------------------------------------ Wok ------------------------------------

def calc_wok(diam, depth):
    matches = []
    for idx, o in enumerate(D.WOK_OPTIONS):
        if o['diamMin'] <= diam <= o['diamMax'] and o['depthMin'] <= depth <= o['depthMax']:
            m = dict(o)
            m['idx'] = idx
            matches.append(m)
    matches.sort(key=lambda m: nozzle_flow(m['nozzle']))
    return {'ok': len(matches) > 0, 'matches': matches}


def wok_result(opt):
    return {
        'nozzles': [{'code': opt['nozzle'], 'qty': opt['qty']}],
        'flowNumber': nozzle_flow(opt['nozzle']) * opt['qty'],
        'heightRange': f"{opt['hmin']} in a {opt['hmax']} in",
        'detail': f"Wok {opt['nozzle']}",
    }


# ------------------------------ Asador de cadena -----------------------------

def calc_chain_broiler(kind, length, width, opening_l=None, opening_w=None):
    opt = D.CHAIN_BROILER_OPTIONS[kind]
    fits = length <= opt['maxLength'] and width <= opt['maxWidth']
    ratio_warning = None
    if kind == 'overhead' and opening_l and opening_w:
        min_l = length * opt['minOpeningRatio']
        min_w = width * opt['minOpeningRatio']
        if opening_l < max(min_l, opt['minOpening']) or opening_w < max(min_w, opt['minOpening']):
            ratio_warning = ('La abertura no cumple el mínimo de 60% de las dimensiones internas '
                              '(o 12x12 in mínimo). Verifique protección horizontal en su lugar.')
    result = None
    if fits:
        result = {
            'nozzles': [{'code': opt['nozzle'], 'qty': opt['qty']}],
            'flowNumber': nozzle_flow(opt['nozzle']) * opt['qty'],
            'heightRange': f"{opt['hmin']} in a {opt['hmax']} in",
            'detail': opt['label'],
        }
    return {'ok': fits, 'opt': opt, 'ratioWarning': ratio_warning, 'result': result}


# ----------------------------- Asador vertical -------------------------------

def calc_upright_broiler(length, width):
    ub = D.UPRIGHT_BROILER
    fits = length <= ub['maxLength'] and width <= ub['maxWidth']
    result = None
    if fits:
        result = {
            'nozzles': [{'code': ub['nozzle'], 'qty': ub['qty']}],
            'flowNumber': nozzle_flow(ub['nozzle']) * ub['qty'],
            'heightRange': '—',
            'detail': ub['label'],
        }
    return {'ok': fits, 'result': result}


# -------------------------------- Salamandra ---------------------------------

def calc_salamander(length, width):
    matches = []
    for i, o in enumerate(D.SALAMANDER_OPTIONS):
        if length <= o['maxLength'] and width <= o['maxWidth']:
            m = dict(o)
            m['idx'] = i
            matches.append(m)
    return {'ok': len(matches) > 0, 'matches': matches}


def salamander_result(opt):
    return {
        'nozzles': [{'code': opt['nozzle'], 'qty': opt['qty']}],
        'flowNumber': nozzle_flow(opt['nozzle']) * opt['qty'],
        'heightRange': '—',
        'detail': opt['label'],
    }


# ---------------------------------- Ducto -------------------------------------

def calc_duct(perimeter, diameter, is_round, qty):
    qty = max(1, int(qty or 1))
    d = D.DUCT_OPTIONS
    if is_round:
        if diameter <= d['single1W']['maxDiameter']:
            base = _duct_res([{'code': '1W', 'qty': 1}], 'Ducto redondo — 1W (una boquilla)')
        elif diameter <= d['single2W']['maxDiameter']:
            base = _duct_res([{'code': '2W', 'qty': 1}], 'Ducto redondo — 2W (una boquilla)')
        else:
            return {'ok': False, 'needsManual': True,
                    'msg': ('Ducto redondo mayor a 32 in de diámetro: no hay opción redonda estándar, '
                            'requiere diseño especial (consulte a ANSUL).')}
    elif perimeter <= d['single1W']['maxPerimeter']:
        base = _duct_res([{'code': '1W', 'qty': 1}], 'Ducto — boquilla única 1W')
    elif perimeter <= d['single2W']['maxPerimeter']:
        base = _duct_res([{'code': '2W', 'qty': 1}], 'Ducto — boquilla única 2W')
    elif perimeter <= d['dual']['maxPerimeter']:
        base = _duct_res([{'code': '1W', 'qty': 1}, {'code': '2W', 'qty': 1}],
                          'Ducto — opción de tres flujos (1W + 2W)')
    else:
        # > 135 in perímetro: aproximación conservadora usando módulos 2W
        # (~35 in de lado B por módulo), redondeado a número par (mitad
        # arriba, mitad abajo).
        approx_nozzles_per_row = math.ceil(perimeter / 2 / 35)
        nozzles_n = max(4, approx_nozzles_per_row * 2)
        base = {
            'ok': True, 'estimated': True,
            'nozzles': [{'code': '2W', 'qty': nozzles_n}],
            'flowNumber': nozzle_flow('2W') * nozzles_n,
            'detail': (f'Ducto grande (perímetro > 135 in) — ESTIMACIÓN conservadora de {nozzles_n} boquillas '
                       '2W por ducto. Verifique manualmente contra las Gráficas 4-1/4-2 del manual R-102 o '
                       'consulte a ANSUL antes de instalar.'),
        }
    return scale_result_by_qty(base, qty, 'ducto')


# ---------------------------------- Pleno -------------------------------------

def calc_plenum(kind, length_ft, plenum_qty):
    plenum_qty = max(1, int(plenum_qty or 1))
    opt = D.PLENUM_OPTIONS[kind]
    nozzle_pairs = math.ceil(length_ft / opt['coveragePerNozzleFt'])
    qty = nozzle_pairs * opt['qty']
    base = {
        'ok': True,
        'nozzles': [{'code': opt['nozzle'], 'qty': qty}],
        'flowNumber': nozzle_flow(opt['nozzle']) * qty,
        'detail': f"{opt['label']} — {length_ft} ft",
    }
    return scale_result_by_qty(base, plenum_qty, 'pleno')


# --------------------------- Precipitador electrostático ----------------------

def calc_precipitator(cells):
    qty = max(1, int(cells or 1))
    return {
        'nozzles': [{'code': '1/2N', 'qty': qty}],
        'flowNumber': nozzle_flow('1/2N') * qty,
        'detail': f'Precipitador electrostático — 1/2N por celda ({qty} celdas)',
    }


# ---------------------- Selección de tanques y cartuchos ----------------------
# Basado en Tank and Cartridge Requirements (pág. 4-77) y System Selection
# Guide (pág. 9-1 a 9-4): cada tanque de 3 gal aporta 11 "flow numbers" de
# capacidad y cada tanque de 1.5 gal aporta 5.

def select_tanks(total_flow):
    if total_flow is None or total_flow <= 0:
        return {'tankCount': 0, 'tanks': [], 'totalGallons': 0, 'n2': None, 'co2': None, 'note': None}
    if total_flow <= 5:
        return {'tankCount': 1, 'tanks': [1.5], 'totalGallons': 1.5, 'n2': D.N2_LT20R, 'co2': D.CO2_101_10, 'note': None}
    if total_flow <= 11:
        return {'tankCount': 1, 'tanks': [3], 'totalGallons': 3, 'n2': D.N2_LT30R, 'co2': D.CO2_101_20, 'note': None}
    # n >= 2 tanques: probar combinación de (n-1) tanques de 3 gal + 1 de
    # 1.5 gal, luego n tanques de 3 gal — se elige la de menor capacidad
    # que alcance.
    for n in range(2, 21):
        cap_a = 11 * (n - 1) + 5
        cap_b = 11 * n
        if total_flow <= cap_a:
            tanks = [3] * (n - 1) + [1.5]
            return {
                'tankCount': n, 'tanks': tanks, 'totalGallons': 3 * (n - 1) + 1.5,
                'n2': D.N2_DOUBLE if n == 2 else 'Ver nota',
                'co2': D.CO2_101_30 if n == 2 else 'Ver nota',
                'note': D.MULTI_CARTRIDGE_NOTE if n >= 3 else None,
            }
        if total_flow <= cap_b:
            tanks = [3] * n
            return {
                'tankCount': n, 'tanks': tanks, 'totalGallons': 3 * n,
                'n2': D.N2_DOUBLE if n == 2 else 'Ver nota',
                'co2': D.CO2_101_30 if n == 2 else 'Ver nota',
                'note': D.MULTI_CARTRIDGE_NOTE if n >= 3 else None,
            }
    return {'tankCount': None, 'tanks': [], 'totalGallons': None,
            'note': 'Flow number excede el máximo tabulado (>220). Requiere diseño especializado — consulte a ANSUL.'}


def tank_counts(tanks):
    counts = {}
    for g in tanks:
        counts[g] = counts.get(g, 0) + 1
    return counts


def tanks_from_manual(tank_list, total_flow=None):
    """Selección MANUAL de tanques (galonaje elegido a mano por el usuario),
    en vez de la selección automática de select_tanks(). Se calcula la
    capacidad real de esa combinación (11 flow numbers por tanque de 3 gal,
    5 por tanque de 1.5 gal) y se avisa si resulta insuficiente para el
    flow number total ya calculado del sistema."""
    tanks = [t for t in (tank_list or []) if t]
    n = len(tanks)
    if n == 0:
        return {'tankCount': 0, 'tanks': [], 'totalGallons': 0, 'n2': None, 'co2': None, 'note': None, 'manual': True}

    total_gallons = sum(tanks)
    capacity = sum(11 if abs(t - 3) < 1e-6 else (5 if abs(t - 1.5) < 1e-6 else 0) for t in tanks)

    if n == 1:
        size = tanks[0]
        if abs(size - 1.5) < 1e-6:
            n2, co2 = D.N2_LT20R, D.CO2_101_10
        elif abs(size - 3) < 1e-6:
            n2, co2 = D.N2_LT30R, D.CO2_101_20
        else:
            n2, co2 = 'Ver nota', 'Ver nota'
        note = None
    elif n == 2:
        n2, co2 = D.N2_DOUBLE, D.CO2_101_30
        note = None
    else:
        n2, co2 = 'Ver nota', 'Ver nota'
        note = D.MULTI_CARTRIDGE_NOTE

    result = {'tankCount': n, 'tanks': tanks, 'totalGallons': total_gallons,
              'n2': n2, 'co2': co2, 'note': note, 'manual': True, 'capacity': capacity}

    if total_flow is not None and total_flow > 0 and total_flow > capacity + 1e-9:
        warning = (f'ADVERTENCIA: la selección manual de tanques (capacidad {fmt_num(capacity)} flow numbers) '
                   f'es INSUFICIENTE para el flow number total calculado de este sistema ({fmt_num(total_flow)}). '
                   'Agregue más tanques o tanques de mayor tamaño antes de instalar.')
        result['note'] = (note + ' ' if note else '') + warning
        result['insufficientCapacity'] = True

    return result


# ------------------------------- Catálogo de modelos ---------------------------

def catalog_entries_for_category(category, custom_catalog):
    manual = [dict(e, source='manual') for e in MODEL_CATALOG if e['category'] == category]
    custom = [dict(e, source='user') for e in (custom_catalog or []) if e['category'] == category]
    return custom + manual


def catalog_entry_to_result(entry):
    if not entry.get('nozzles'):
        return None
    hmin, hmax = entry.get('hmin'), entry.get('hmax')
    if hmin is not None and hmax is not None:
        height_range = f'{hmin} a {hmax} in'
    elif hmin is not None:
        height_range = f'{hmin} in'
    else:
        height_range = '—'
    source_txt = 'Datos de catálogo (agregado por ti)' if entry.get('source') == 'user' else 'Datos de catálogo'
    notes = entry.get('notes') or ''
    return {
        'nozzles': entry['nozzles'],
        'flowNumber': catalog_flow_number(entry['nozzles']),
        'heightRange': height_range,
        'detail': f"{source_txt} — {entry.get('brand', '')} {entry.get('model', '')}." + (f' {notes}' if notes else ''),
    }


# --------------------------- Resúmenes (agregados) ------------------------------

def kitchen_summary(kitchen):
    nozzle_totals = {}
    total_flow = 0
    rows = []
    for item in kitchen.get('equipment', []):
        r = item.get('result')
        if not r:
            continue
        total_flow += r.get('flowNumber') or 0
        for n in r.get('nozzles') or []:
            nozzle_totals[n['code']] = nozzle_totals.get(n['code'], 0) + n['qty']
        rows.append(item)

    override = kitchen.get('tankOverride')
    if override and override.get('enabled') and override.get('tanks'):
        tanks = tanks_from_manual(override['tanks'], total_flow)
    else:
        tanks = select_tanks(total_flow)

    return {'totalFlow': total_flow, 'nozzleTotals': nozzle_totals, 'tanks': tanks,
            'itemCount': len(kitchen.get('equipment', [])), 'rows': rows}


def project_summary(project):
    nozzle_totals = {}
    total_gallons = 0
    total_tanks = 0
    total_flow = 0
    kitchen_summaries = []
    for k in project.get('kitchens', []):
        s = kitchen_summary(k)
        kitchen_summaries.append({'kitchen': k, 'summary': s})
        for code, qty in s['nozzleTotals'].items():
            nozzle_totals[code] = nozzle_totals.get(code, 0) + qty
        total_gallons += s['tanks'].get('totalGallons') or 0
        total_tanks += s['tanks'].get('tankCount') or 0
        total_flow += s.get('totalFlow') or 0
    return {'nozzleTotals': nozzle_totals, 'totalGallons': total_gallons, 'totalTanks': total_tanks,
            'totalFlow': total_flow, 'kitchenSummaries': kitchen_summaries}
