# -*- coding: utf-8 -*-
"""
Pruebas del motor Buckeye Kitchen Mister (BFR-TM Rev. 6) y del registro de
marcas. Cada caso cita la página del manual de donde sale el valor esperado.

Ejecutar:  python -m tests.test_buckeye      (o todas:  python -m tests)
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ansul import systems
from ansul.store import Store
from ansul.systems.buckeye_bfr import data as BD
from ansul.systems.buckeye_bfr import engine as BE
from ansul.systems.buckeye_bfr import category_defs as BC


def check(label, cond):
    status = 'OK  ' if cond else 'FAIL'
    print(f'[{status}] {label}')
    if not cond:
        raise AssertionError(label)


def _compute(cat, values):
    return BC.CATEGORY_DEFS[cat]['compute'](values)


def _opts(calc):
    return [(m['id'], m['nozzle'], m['modulesCount']) for m in calc['matches']]


# ------------------------------- Datos ----------------------------------------

def test_nozzle_flow_points_p2_9():
    expected = {'N-1HP': (1, 'Azul'), 'N-1LP': (1, 'Rojo'), 'N-2HP': (2, 'Verde'),
                'N-2LP': (2, 'Amarillo'), 'N-2W': (2, 'Blanco')}
    for code, (fp, color) in expected.items():
        check(f'p. 2-9: {code} = {fp} flow point(s), banda {color}',
              BD.NOZZLES[code]['flow'] == fp and BD.NOZZLES[code]['color'] == color)


def test_cylinders_p2_1_and_piping_p3_13():
    for size, model, bracket, pipe in [(5, 'BFR-5', 'MB-1', 1500), (10, 'BFR-10', 'MB-2', 2500),
                                       (15, 'BFR-15', 'MB-2', 2800), (20, 'BFR-20', 'MB-2', 2800)]:
        c = BD.CYLINDERS[size]
        check(f'p. 2-1 / 3-13: {model} = {size} FP, soporte {bracket}, {pipe} mL máx.',
              c['model'] == model and c['flow'] == size and c['bracket'] == bracket and c['maxPipeMl'] == pipe)
    check('p. 3-13: volumen 1/2 in = 59.8 mL/ft', BD.PIPE_VOLUME_ML_PER_FT['1/2'] == 59.8)


# ------------------------------ Estufas ---------------------------------------

def test_range_24x24_all_options():
    c = _compute('range', {'width': '24', 'depth': '24', 'backShelf': False})
    opts = _opts(c)
    check('Estufa 24x24 -> N-1LP alta proximidad, 1 boquilla (p. 3-4)', ('R4_HP', 'N-1LP', 1) in opts)
    check('Estufa 24x24 -> N-2W baja proximidad, 1 boquilla (p. 3-4)', ('R4_LP', 'N-2W', 1) in opts)
    check('Estufa 24x24 -> también 2 módulos de 12x24 con N-1LP (p. 3-3 + 3-11)', ('R2_LP', 'N-1LP', 2) in opts)
    check('Estufa 24x24 -> opción de 6 quemadores también cabe (36x24)', ('R6', 'N-2LP', 1) in opts)
    check('Estufa 24x24 sin repisa -> NO ofrece la cobertura de repisa alta proximidad',
          all(o[0] != 'R4_BS_HP' for o in opts))
    check('Primera opción = la de menos flow points (1 FP)', c['matches'][0]['totalFlow'] == 1)


def test_range_back_shelf_filters_options():
    c = _compute('range', {'width': '24', 'depth': '24', 'backShelf': True})
    ids = {m['id'] for m in c['matches']}
    check('Estufa con repisa -> solo renglones * / *** de la p. 3-12', ids == {'R2_LP', 'R4_LP', 'R4_BS_HP'})


def test_range_six_burner_36x24():
    c = _compute('range', {'width': '36', 'depth': '24'})
    opts = _opts(c)
    check('Estufa 36x24 -> N-2LP una boquilla (p. 3-4)', ('R6', 'N-2LP', 1) in opts)
    check('Estufa 36x24 -> o 2 × N-1LP alta proximidad (módulos de 18x24)', ('R4_HP', 'N-1LP', 2) in opts)
    check('Estufa 36x24 -> o 3 × N-1LP de 12x24', ('R2_LP', 'N-1LP', 3) in opts)


def test_range_depth_over_24_needs_modules():
    c = _compute('range', {'width': '24', 'depth': '30'})
    m = next(m for m in c['matches'] if m['id'] == 'R4_HP')
    check('Estufa 24 ancho x 30 fondo -> 2 módulos (1 × 2) con N-1LP', (m['cols'], m['rows']) == (1, 2))


# ---------------------------- Freidoras ---------------------------------------

def test_fryer_single_nozzle_p3_7():
    c = _compute('fryer', {'width': '20.25', 'depth': '24'})
    r = BC.CATEGORY_DEFS['fryer']['result_from_choice'](c, 0)
    check('Freidora 20.25x24 -> 1 × N-2HP (p. 3-7)', r['nozzles'] == [{'code': 'N-2HP', 'qty': 1}])
    check('Freidora 20.25x24 -> 2 flow points', r['flowNumber'] == 2)
    check('Freidora -> altura 24 a 45 in', r['heightRange'] == '24 a 45 in')


def test_fryer_modular_and_864_limit():
    c = _compute('fryer', {'width': '36', 'depth': '24'})   # 864 in² justo en el límite
    check('Freidora 36x24 (864 in²) -> 2 módulos N-2HP', _opts(c) == [('F', 'N-2HP', 2)])
    c = _compute('fryer', {'width': '40', 'depth': '24'})   # 960 in²
    check('Freidora 40x24 (960 in² > 864) -> no se puede modularizar (p. 3-7)',
          c['ok'] is False and c['overModularLimit'] is True)
    check('Mensaje de 864 in²', '864' in BC.CATEGORY_DEFS['fryer']['not_fit_msg']({}, c))


def test_fryer_orientation_is_not_rotated():
    # DISEÑO.md 5.1: el programa no gira la cobertura (20.25 ancho × 24 fondo).
    c = _compute('fryer', {'width': '24', 'depth': '20'})
    check('Freidora 24 ancho x 20 fondo -> 2 módulos (no se gira la cobertura)', c['matches'][0]['modulesCount'] == 2)


# ------------------------------ Planchas --------------------------------------

def test_griddle_options_p3_7_to_3_9():
    c = _compute('griddle', {'width': '42', 'depth': '30'})
    ids = {(m['id'], m['modulesCount']) for m in c['matches']}
    check('Plancha 42x30 -> estándar N-1LP (p. 3-7)', ('G_STD', 1) in ids)
    check('Plancha 42x30 -> extra baja proximidad N-2W (p. 3-9)', ('G_XLP', 1) in ids)
    check('Plancha 42x30 -> grande N-1LP (48x30) también cabe', ('G_LG', 1) in ids)
    c = _compute('griddle', {'width': '60', 'depth': '30'})
    opts = _opts(c)
    check('Plancha 60x30 -> N-2LP una boquilla (p. 3-8)', ('G_XL', 'N-2LP', 1) in opts)
    check('Plancha 60x30 -> N-2W baja proximidad (p. 3-9)', ('G_LP', 'N-2W', 1) in opts)
    check('Plancha 60x30 -> o 2 × N-1LP estándar', ('G_STD', 'N-1LP', 2) in opts)


# ------------------------------ Asadores --------------------------------------

def test_charbroiler_example_fig_3_24():
    # Figura 3-24 (p. 3-11): asador radiante de 60 x 24 protegido con 2 módulos de 30 x 24.
    c = _compute('charbroiler', {'kind': 'radiant', 'width': '60', 'depth': '24'})
    m = c['matches'][0]
    check('Asador radiante 60x24 -> 2 × N-1HP (Fig. 3-24)', (m['nozzle'], m['modulesCount']) == ('N-1HP', 2))
    check('Asador radiante 60x24 -> módulos de 30 x 24', (m['moduleW'], m['moduleD']) == (30, 24))


def test_charbroiler_lava_and_solid_fuel():
    c = _compute('charbroiler', {'kind': 'lava', 'width': '24', 'depth': '24'})
    check('Asador lava rock 24x24 -> N-2HP (p. 3-10)', _opts(c) == [('C_LAVA', 'N-2HP', 1)])
    c = _compute('charbroiler', {'kind': 'solid', 'width': '24', 'depth': '24', 'fuelDepth': '7'})
    check('Combustible sólido con 7 in de leña -> no cumple (máx. 6 in, p. 3-11)', c.get('fuelTooDeep') is True)


def test_upright_broiler_not_modularized():
    c = _compute('uprightbroiler', {'width': '36', 'depth': '24'})
    check('Salamandra 36x24 -> 1 × N-1LP (p. 3-10)', _opts(c) == [('UB', 'N-1LP', 1)])
    c = _compute('uprightbroiler', {'width': '40', 'depth': '24'})
    check('Salamandra 40x24 -> no cabe y no se modulariza', c['ok'] is False)


def test_wok_range_p3_6():
    check('Wok 20 in -> N-1HP', BE.calc_wok(20)['result']['nozzles'] == [{'code': 'N-1HP', 'qty': 1}])
    check('Wok 11 in -> fuera de cobertura (mín. 12)', BE.calc_wok(11)['ok'] is False)
    check('Wok 31 in -> fuera de cobertura (máx. 30)', BE.calc_wok(31)['ok'] is False)


# --------------------------- Ductos y plenos -----------------------------------

def test_duct_p3_1():
    r = BE.calc_duct(16, 8)          # perímetro 48, lado 16 <= 16.75
    check('Ducto 16x8 -> N-1LP', r['nozzles'] == [{'code': 'N-1LP', 'qty': 1}])
    r = BE.calc_duct(12, 12)         # perímetro 48
    check('Ducto 12x12 -> N-1LP', r['nozzles'][0]['code'] == 'N-1LP')
    r = BE.calc_duct(18, 6)          # perímetro 48 pero lado 18 > 16.75
    check('Ducto 18x6 -> N-2W (lado mayor > 16-3/4 in)', r['nozzles'][0]['code'] == 'N-2W')
    r = BE.calc_duct(37.5, 37.5)     # perímetro 150
    check('Ducto 37.5x37.5 (150 in) -> 1 × N-2W', r['nozzles'] == [{'code': 'N-2W', 'qty': 1}])
    r = BE.calc_duct(50, 30)         # perímetro 160 > 150
    check('Ducto 50x30 (160 in) -> 2 × N-2W en áreas iguales (p. 3-2)', r['nozzles'] == [{'code': 'N-2W', 'qty': 2}])
    r = BE.calc_duct(diameter=15, is_round=True)
    check('Ducto redondo Ø15 -> N-1LP', r['nozzles'][0]['code'] == 'N-1LP')
    r = BE.calc_duct(diameter=16, is_round=True)
    check('Ducto redondo Ø16 (50.3 in circ.) -> N-2W (DISEÑO.md 5.2)', r['nozzles'][0]['code'] == 'N-2W')
    r = BE.calc_duct(diameter=50, is_round=True)
    check('Ducto redondo Ø50 -> sin protección estándar', r['ok'] is False and r.get('needsManual'))


def test_duct_qty_and_precipitator():
    c = _compute('duct', {'sideA': '16', 'sideB': '8', 'qty': '2'})
    check('2 ductos idénticos 16x8 -> 2 × N-1LP, 2 FP', c['result']['nozzles'] == [{'code': 'N-1LP', 'qty': 2}]
          and c['result']['flowNumber'] == 2)
    c = _compute('precipitator', {'sideA': '16', 'sideB': '8'})
    check('Precipitador -> boquilla de ducto arriba y abajo (p. 3-2)', c['result']['nozzles'] == [{'code': 'N-1LP', 'qty': 2}])


def test_plenum_p3_3():
    c = _compute('plenum', {'kind': 'single', 'lengthM': '3.6', 'widthM': '1.2'})
    check('Pleno 3.6 m (11.8 ft) -> 1 × N-1HP', c['result']['nozzles'] == [{'code': 'N-1HP', 'qty': 1}])
    c = _compute('plenum', {'kind': 'vbank', 'lengthM': str(16 * 0.3048), 'widthM': '1'})
    check('Pleno 16 ft -> 2 × N-1HP en tramos de 8 ft (p. 3-3)',
          c['result']['nozzles'] == [{'code': 'N-1HP', 'qty': 2}] and '8 ft' in c['result']['detail'])
    c = _compute('plenum', {'kind': 'single', 'lengthM': '3', 'widthM': '1.5'})
    check('Pleno de 1.5 m de ancho (> 4 ft) -> no cumple', c['ok'] is False and c.get('widthExceeded'))


# ------------------------------ Cilindros -------------------------------------

def test_cylinder_combinations_22_fp():
    combos = BE.cylinder_combinations(22, 0)
    got = [tuple(c['cylinders']) for c in combos]
    expected = [(20, 5), (15, 10), (15, 5, 5), (10, 10, 5), (10, 5, 5, 5), (5, 5, 5, 5, 5),
                (20, 10), (15, 15), (10, 10, 10), (20, 15), (20, 20)]
    check('22 FP -> las 11 combinaciones mínimas, ordenadas por sobrante y número de cilindros', got == expected)


def test_cylinder_two_fp_nozzles_cannot_split():
    combos = [tuple(c['cylinders']) for c in BE.cylinder_combinations(0, 5)]   # 5 × N-2HP = 10 FP
    check('5 boquillas de 2 FP no caben en 2 × BFR-5 (cada uno solo admite 2 boquillas)', (5, 5) not in combos)
    check('5 boquillas de 2 FP -> BFR-10 es la primera opción', combos[0] == (10,))
    check('5 boquillas de 2 FP -> 3 × BFR-5 también es válido', (5, 5, 5) in combos)


def test_kitchen_summary_and_choice():
    k = {'equipment': [
        {'category': 'fryer', 'result': {'nozzles': [{'code': 'N-2HP', 'qty': 1}], 'flowNumber': 2}},
        {'category': 'duct', 'result': {'nozzles': [{'code': 'N-1LP', 'qty': 1}], 'flowNumber': 1}},
    ]}
    s = BE.kitchen_summary(k)
    check('Resumen: 3 flow points', s['totalFlow'] == 3)
    check('Resumen: primera opción BFR-5', s['chosen']['cylinders'] == [5])
    check('Resumen: avisa requisitos mínimos de tubería (hay freidora)', any('360 mL' in n for n in s['notes']))
    k['cylinderChoice'] = [10]
    check('Elegir BFR-10 para 3 FP es válido y se respeta', BE.kitchen_summary(k)['chosen']['cylinders'] == [10])
    k['cylinderChoice'] = [5, 5]
    s = BE.kitchen_summary(k)
    check('2 × BFR-5 para 3 FP sobra un cilindro -> se avisa y se usa la primera opción',
          s['chosen']['cylinders'] == [5] and any('ya no es válida' in n for n in s['notes']))
    k2 = {'equipment': [{'category': 'wok', 'result': {'nozzles': [{'code': 'N-1HP', 'qty': 1}], 'flowNumber': 1}}]}
    check('Sistema con wok y 1 FP -> advertencia de mínimo 3 FP (p. 3-13)',
          any('mínimo es 3' in n for n in BE.kitchen_summary(k2)['notes']))
    k3 = {'equipment': [{'category': 'duct', 'result': {'nozzles': [{'code': 'N-1LP', 'qty': 1}], 'flowNumber': 1}}]}
    check('Sistema solo con ducto -> sin advertencia de mínimos', BE.kitchen_summary(k3)['notes'] == [])


# --------------------------- Registro y store ----------------------------------

def test_registry():
    check('Registro: ANSUL por defecto', systems.get(None).key == 'ansul_r102')
    check('Registro: proyecto Buckeye', systems.for_project({'system': 'buckeye_bfr'}).key == 'buckeye_bfr')
    check('Registro: flow points en Buckeye', systems.get('buckeye_bfr').flow_label == 'Flow points')
    for key, s in systems.REGISTRY.items():
        check(f'{key}: todas las categorías tienen definición', set(s.category_order) == set(s.category_defs))


def test_store_migration_and_brand_rules():
    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, 'db.json')
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump({'projects': [{'id': 'p1', 'name': 'Viejo', 'kitchens': []}]}, f)
        st = Store(path=ruta)
        st.load()
        check('load(): proyecto sin marca -> ansul_r102', st.data['projects'][0]['system'] == 'ansul_r102')
        with open(ruta, encoding='utf-8') as f:
            check('load(): la migración se guardó en el archivo', json.load(f)['projects'][0]['system'] == 'ansul_r102')

        p = st.add_project('Nuevo', 'buckeye_bfr')
        check('add_project con marca Buckeye', p['system'] == 'buckeye_bfr')
        st.set_project_system(p['id'], 'ansul_r102')
        check('Se puede cambiar la marca si no hay riesgos', st.get_project(p['id'])['system'] == 'ansul_r102')
        st.set_project_system(p['id'], 'buckeye_bfr')
        k = st.add_kitchen(p['id'], 'Campana 1')
        st.add_equipment(p['id'], k['id'], {'category': 'wok', 'input': {'diam': 20},
                                            'result': BE.calc_wok(20)['result']})
        try:
            st.set_project_system(p['id'], 'ansul_r102')
            changed = True
        except ValueError:
            changed = False
        check('NO se puede cambiar la marca si ya hay riesgos', changed is False)
        try:
            st.add_project('X', 'marca_inexistente')
            ok = True
        except ValueError:
            ok = False
        check('Marca desconocida -> error', ok is False)

        st.set_kitchen_cylinder_choice(p['id'], k['id'], [5, 10])
        check('Se guarda la combinación de cilindros (ordenada)', st.get_kitchen(p['id'], k['id'])['cylinderChoice'] == [10, 5])
        dup = st.duplicate_kitchen(p['id'], k['id'])
        check('Duplicar sistema copia la combinación de cilindros', dup['cylinderChoice'] == [10, 5])


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_') and callable(v)]
    for t in tests:
        t()
    print(f'\n{len(tests)} pruebas de Buckeye pasaron correctamente.')


if __name__ == '__main__':
    run_all()
