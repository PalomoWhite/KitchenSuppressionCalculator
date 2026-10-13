# -*- coding: utf-8 -*-
"""
Pruebas de regresión del motor de cálculo (ansul.engine / ansul.category_defs).

No requieren PySide6 ni entorno gráfico — solo validan que la lógica de
cálculo (boquillas, flow numbers, selección de tanques) se comporte como
se espera para una serie de casos de referencia tomados del manual ANSUL
R-102 y de la Hoja Resumen F-2015158-01_LAS.

Ejecutar con:  python -m pytest tests/ (o simplemente: python tests/test_engine.py)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ansul import engine as E
from ansul import category_defs as CD
from ansul import data as D


def check(label, cond):
    status = 'OK  ' if cond else 'FAIL'
    print(f'[{status}] {label}')
    if not cond:
        raise AssertionError(label)


def test_fryer_group_a():
    c = CD.CATEGORY_DEFS['fryer']['compute']({'hasDripboard': False, 'frypotD': '14', 'frypotL': '15', 'modules': 1})
    r = E.fryer_result_for_choice(c, 0)
    check('Freidora 14x15 sin escurridor -> boquilla 290', r['nozzles'][0]['code'] == '290')
    check('Freidora 14x15 -> flow number 2', r['flowNumber'] == 2)


def test_fryer_area_limit():
    # 30 x 30 = 900 in^2 > 864 in^2 (límite absoluto de modularización)
    c = CD.CATEGORY_DEFS['fryer']['compute']({'hasDripboard': False, 'frypotD': '30', 'frypotL': '30', 'modules': 1})
    check('Freidora que excede 864 in^2 -> ok=False', c['ok'] is False)
    check('Freidora que excede 864 in^2 -> overLimit=True', c['overLimit'] is True)


def test_fryer_230_option_available():
    # Manual R-102, pág. 4-8 ("Maximum Area Dimensions – Single Nozzle
    # Fryer Protection"): tina 14x15 in (sin escurridor) / 14x21 in en
    # total (con escurridor) admite boquilla 230 a una altura de 27 a 47
    # in de alta proximidad — además de 245 (20-27 in) y 290 (13-16 in)
    # para la misma tina. Antes de esta corrección, un grupo distinto
    # (tina más grande, 19.5x19 in) que también admite 290 a 13-16 in
    # duplicaba esa opción en la lista de boquillas.
    c = CD.CATEGORY_DEFS['fryer']['compute']({'hasDripboard': False, 'frypotD': '14', 'frypotL': '15', 'modules': 1})
    codes = [(m['nozzle'], m['hmin'], m['hmax']) for m in c['matches']]
    check('Freidora 14x15 sin escurridor -> incluye boquilla 230 (27-47 in)', ('230', 27, 47) in codes)
    check('Freidora 14x15 sin escurridor -> incluye boquilla 245 (20-27 in)', ('245', 20, 27) in codes)
    check('Freidora 14x15 sin escurridor -> sin boquillas duplicadas', len(codes) == len(set(codes)))

    c2 = CD.CATEGORY_DEFS['fryer']['compute']({'hasDripboard': True, 'frypotD': '14', 'frypotL': '14',
                                                'overallD': '14', 'overallL': '21', 'modules': 1})
    codes2 = [(m['nozzle'], m['hmin'], m['hmax']) for m in c2['matches']]
    check('Freidora 14x14 con escurridor (total 14x21) -> incluye boquilla 230 (27-47 in)',
          ('230', 27, 47) in codes2)
    check('Freidora con escurridor -> no se modulariza (queda en 1 zona)', c2['modules'] == 1)


def test_wok_only_second_option_fits():
    # Diámetro 12 in: la boquilla 260 requiere diamMin=14, solo cabe 1N.
    # (Antes de la corrección, esto causaba un StopIteration/crash.)
    c = E.calc_wok(12, 5)
    check('Wok 12 in de diámetro -> solo 1 opción', len(c['matches']) == 1)
    r = CD.CATEGORY_DEFS['wok']['result_from_choice'](c, 0)
    check('Wok 12 in -> boquilla 1N (sin crash)', r['nozzles'][0]['code'] == '1N')


def test_salamander_positional_choice():
    # Corregido: antes usaba length=30 (fondo) x width=15 (ancho), lo que invertía
    # la orientación del manual (pág. 4-24). Lo que se quería probar es una
    # salamandra de 30 in de ancho x 15 in de fondo -> 2 opciones (1F y 1N local).
    c = CD.CATEGORY_DEFS['salamander']['compute']({'length': '15', 'width': '30'})
    check('Salamandra 15 fondo x 30 ancho -> 2 opciones disponibles', len(c['matches']) == 2)
    r0 = CD.CATEGORY_DEFS['salamander']['result_from_choice'](c, 0)
    r1 = CD.CATEGORY_DEFS['salamander']['result_from_choice'](c, 1)
    check('Salamandra opción 0 distinta de opción 1', r0['detail'] != r1['detail'])


def test_duct_round_vs_rect():
    r_round = E.calc_duct(None, 20, True, 1)
    check('Ducto redondo 20 in diám -> 2W', r_round['nozzles'][0]['code'] == '2W')
    r_rect = E.calc_duct(120, None, False, 1)
    check('Ducto rectangular perímetro 120 -> 1W+2W', {n['code'] for n in r_rect['nozzles']} == {'1W', '2W'})


def test_select_tanks_breakpoints():
    check('flow=5 -> 1 tanque de 1.5 gal', E.select_tanks(5)['tanks'] == [1.5])
    check('flow=11 -> 1 tanque de 3 gal', E.select_tanks(11)['tanks'] == [3])
    check('flow=16 -> tanques 3+1.5 gal', E.select_tanks(16)['tanks'] == [3, 1.5])
    check('flow=22 -> 2 tanques de 3 gal', E.select_tanks(22)['tanks'] == [3, 3])
    check('flow=23 -> 3 tanques (nota multi-cartucho)', E.select_tanks(23)['note'] is not None)


def test_range_burners_is_informational_only():
    # El número de quemadores ya NO restringe ni fuerza ninguna boquilla —
    # el manual R-102 no distingue por número de quemadores, solo por las
    # medidas del área de cocción (Nozzle Application Chart, pág. 4-30/4-31).
    base = {'d1': '30', 'd2': '10', 'modules': 1}
    c4 = CD.CATEGORY_DEFS['range']['compute'](dict(base, burners='4'))
    c6 = CD.CATEGORY_DEFS['range']['compute'](dict(base, burners='6'))
    check('Estufa: 4 y 6 quemadores dan exactamente las mismas opciones',
          [m['nozzle'] for m in c4['matches']] == [m['nozzle'] for m in c6['matches']])
    check('Estufa 6 quemadores -> sigue incluyendo opciones de 1 sola boquilla',
          any(m['qty'] == 1 for m in c6['matches']))
    check('Estufa 6 quemadores -> también incluye la opción de 2 boquillas',
          any(m['qty'] == 2 for m in c6['matches']))


def test_range_one_burner_option_available():
    specs = CD.CATEGORY_DEFS['range']['fields']({'burners': '1'})
    burner_field = next(f for f in specs if f['key'] == 'burners')
    check("Estufa admite opción '1 quemador'", any(o['value'] == '1' for o in burner_field['options']))


def test_range_fuel_is_informational_only():
    base = {'d1': '30', 'd2': '10', 'modules': 1, 'burners': '4'}
    c_gas = CD.CATEGORY_DEFS['range']['compute'](dict(base, fuel='gas'))
    c_wood = CD.CATEGORY_DEFS['range']['compute'](dict(base, fuel='wood'))
    check('Estufa: el combustible no cambia las boquillas calculadas',
          [m['nozzle'] for m in c_gas['matches']] == [m['nozzle'] for m in c_wood['matches']])


def test_range_auto_modularizes_oversized_equipment():
    # 56x10 in no cabe en ninguna opción de una sola zona (el lado más largo
    # máximo de toda la tabla de Estufa es 36 in), pero sí modularizando
    # automáticamente en 2 zonas de 28 in cada una.
    c = CD.CATEGORY_DEFS['range']['compute']({'d1': '56', 'd2': '10', 'modules': 1})
    check('Estufa 56x10 se modulariza automáticamente en 2 zonas', c['ok'] is True and c['modules'] == 2)
    codes = {m['nozzle'] for m in c['matches']}
    check('Estufa modularizada -> ofrece varias boquillas/proximidades, no solo una fija',
          len(codes) > 1)
    m_1n = next(m for m in c['matches'] if m['nozzle'] == '1N')
    idx = c['matches'].index(m_1n)
    r = CD.CATEGORY_DEFS['range']['result_from_choice'](c, idx)
    check('Estufa modularizada con 1N (alta proximidad) -> 2 boquillas totales (1 por zona x 2 zonas)',
          r['nozzles'][0]['qty'] == 2)
    check("Detalle del resultado menciona la modularización", 'modularizado' in r['detail'])


def test_tiltskillet_auto_modularizes_into_zones():
    # 40x20 in no cabe en ninguna caja de un solo módulo de freidora, pero sí
    # dividiéndolo en 3 zonas — exactamente el método que pide el manual
    # para sartenes de volteo (pág. 4-12): dividir el equipo en zonas según
    # el número de boquillas necesario.
    c = CD.CATEGORY_DEFS['tiltskillet']['compute']({'d1': '40', 'd2': '20', 'modules': 1})
    check('Sartén de volteo 40x20 se modulariza automáticamente', c['ok'] is True and c['modules'] > 1)
    r = CD.CATEGORY_DEFS['tiltskillet']['result_from_choice'](c, 0)
    check('Sartén de volteo modularizado -> boquillas totales = número de zonas',
          r['nozzles'][0]['qty'] == c['modules'])


def test_robata_charcoal_and_wood():
    c = CD.CATEGORY_DEFS['robata']['compute']({'fuel': 'charcoal', 'd1': '15', 'd2': '15'})
    check('Robata carbón 15x15 -> encuentra opción', len(c['matches']) > 0)
    r = CD.CATEGORY_DEFS['robata']['result_from_choice'](c, 0)
    check('Robata carbón -> boquilla 1N', r['nozzles'][0]['code'] == '1N')

    c2 = CD.CATEGORY_DEFS['robata']['compute']({'fuel': 'wood', 'd1': '25', 'd2': '25'})
    check('Robata leña 25x25 -> encuentra opción', len(c2['matches']) > 0)
    r2 = CD.CATEGORY_DEFS['robata']['result_from_choice'](c2, 0)
    check('Robata leña -> boquilla 3N', r2['nozzles'][0]['code'] == '3N')


def test_plenum_in_meters():
    # vertical1W: coveragePerNozzleFt=4, maxWidthFt=4 (~1.22 m)
    c_ok = CD.CATEGORY_DEFS['plenum']['compute']({'kind': 'vertical1W', 'lengthM': '2.44', 'widthM': '1', 'qty': 1})
    check('Pleno vertical 2.44 m de largo, 1 m de ancho -> ok', c_ok['ok'] is True)
    check('Pleno vertical -> flow number > 0', c_ok['result']['flowNumber'] > 0)

    c_bad = CD.CATEGORY_DEFS['plenum']['compute']({'kind': 'vertical1W', 'lengthM': '2', 'widthM': '2', 'qty': 1})
    check('Pleno vertical con ancho > 1.22 m -> ok=False (excede máximo)', c_bad['ok'] is False)
    check('Pleno vertical con ancho excedido -> widthExceeded=True', c_bad.get('widthExceeded') is True)


def test_tanks_from_manual_override():
    manual = E.tanks_from_manual([3, 3], total_flow=20)
    check('Selección manual 2 tanques de 3 gal -> capacidad suficiente (sin advertencia)',
          manual.get('insufficientCapacity') is not True)
    check('Selección manual 2 tanques de 3 gal -> cartucho N2 doble', manual['n2'] == D.N2_DOUBLE)

    insufficient = E.tanks_from_manual([1.5], total_flow=20)
    check('Selección manual insuficiente -> se marca insufficientCapacity',
          insufficient.get('insufficientCapacity') is True)

    kitchen = {'equipment': [{'result': {'nozzles': [{'code': '290', 'qty': 1}], 'flowNumber': 2}}],
               'tankOverride': {'enabled': True, 'tanks': [3]}}
    s = E.kitchen_summary(kitchen)
    check('kitchen_summary respeta el override manual de tanques', s['tanks']['manual'] is True)
    check('kitchen_summary con override -> tanques = [3]', s['tanks']['tanks'] == [3])


def test_ft_m_conversion():
    check('1 m ≈ 3.28084 ft', abs(E.m_to_ft(1) - 3.28084) < 0.001)
    check('1 ft ≈ 0.3048 m', abs(E.ft_to_m(1) - 0.3048) < 0.0001)
    check('Ida y vuelta ft->m->ft preserva el valor', abs(E.m_to_ft(E.ft_to_m(12)) - 12) < 1e-6)


def test_in_cm_conversion():
    check('1 in = 2.54 cm', abs(E.in_to_cm(1) - 2.54) < 1e-9)
    check('1 cm ≈ 0.393701 in', abs(E.cm_to_in(1) - 0.393701) < 0.0001)
    check('Ida y vuelta in->cm->in preserva el valor', abs(E.cm_to_in(E.in_to_cm(20)) - 20) < 1e-6)


def test_dimensions_display():
    fryer_sin_escurridor = {'category': 'fryer', 'input': {'hasDripboard': False, 'frypotD': '14', 'frypotL': '15'}}
    check('Freidora sin escurridor -> "14 x 15 in" (largo x ancho)',
          CD.dimensions_display(fryer_sin_escurridor) == '14 x 15 in')

    fryer_con_escurridor = {'category': 'fryer', 'input': {
        'hasDripboard': True, 'frypotD': '14', 'frypotL': '15', 'overallD': '21', 'overallL': '15'}}
    check('Freidora con escurridor -> usa las medidas totales, no las de la tina',
          CD.dimensions_display(fryer_con_escurridor) == '21 x 15 in')

    tiltskillet = {'category': 'tiltskillet', 'input': {'d1': '20', 'd2': '40'}}
    check('Sartén de volteo -> "Largo x Ancho" = d2 x d1',
          CD.dimensions_display(tiltskillet) == '40 x 20 in')

    wok = {'category': 'wok', 'input': {'diam': '12', 'depth': '5'}}
    check('Wok -> se muestra como diámetro (Ø), no largo x ancho', CD.dimensions_display(wok) == 'Ø12 in')

    duct_round = {'category': 'duct', 'input': {'round': True, 'diameter': '20', 'qty': '1'}}
    check('Ducto redondo -> diámetro', CD.dimensions_display(duct_round) == 'Ø20 in')

    duct_rect = {'category': 'duct', 'input': {'round': False, 'sideA': '10', 'sideB': '8', 'qty': '1'}}
    check('Ducto rectangular -> Ancho x Alto', CD.dimensions_display(duct_rect) == '10 x 8 in')

    plenum = {'category': 'plenum', 'input': {'lengthM': '2.44', 'widthM': '1'}}
    check('Pleno -> Largo x Ancho en metros', CD.dimensions_display(plenum) == '2.44 x 1 m')

    combi = {'category': 'combioven', 'input': {}}
    check('Horno Combi -> sin medidas de footprint (None)', CD.dimensions_display(combi) is None)

    kettle = {'category': 'kettle', 'input': {}}
    check('Marmita -> sin medidas de footprint (None)', CD.dimensions_display(kettle) is None)

    fryer_sin_datos = {'category': 'fryer', 'input': {}}
    check('Sin medidas capturadas -> None', CD.dimensions_display(fryer_sin_datos) is None)


def test_kettle_no_protection_required():
    # La marmita, igual que el horno combi, se registra solo como
    # referencia: no aparece en el catálogo de boquillas del manual R-102
    # porque no genera vapores grasosos (cocina con agua/vapor, no aceite).
    check('Marmita está en el orden de categorías', 'kettle' in D.CATEGORY_ORDER)
    check('Marmita tiene etiqueta bilingüe', D.CATEGORY_LABELS['kettle'] == 'Marmita / Kettle')

    cdef = CD.CATEGORY_DEFS['kettle']
    check('Marmita no requiere campos obligatorios', cdef['required_fields']({}) == [])
    check('Marmita -> has_required_inputs siempre True (nada que capturar)',
          CD.has_required_inputs('kettle', {}) is True)

    c = cdef['compute']({})
    check('Marmita -> compute() ok=True', c['ok'] is True)
    check('Marmita -> sin boquillas', c['result']['nozzles'] == [])
    check('Marmita -> flow number 0', c['result']['flowNumber'] == 0)


def test_depth_display():
    wok = {'category': 'wok', 'input': {'diam': '12', 'depth': '5'}}
    check('Wok -> profundidad se muestra por separado de "Largo x Ancho"', CD.depth_display(wok) == '5 in')

    robata_con_profundidad = {'category': 'robata', 'input': {'d1': '15', 'd2': '15', 'depth': '3'}}
    check('Robata con profundidad capturada -> "3 in"', CD.depth_display(robata_con_profundidad) == '3 in')

    robata_sin_profundidad = {'category': 'robata', 'input': {'d1': '15', 'd2': '15'}}
    check('Robata sin profundidad (opcional, sin capturar) -> None',
          CD.depth_display(robata_sin_profundidad) is None)

    grill = {'category': 'grill', 'input': {'d1': '20', 'd2': '30', 'depth': '2'}}
    check('Parrilla con profundidad de cama -> "2 in"', CD.depth_display(grill) == '2 in')

    range_sin_profundidad = {'category': 'range', 'input': {'d1': '20', 'd2': '30'}}
    check('Estufa no tiene campo de profundidad -> None', CD.depth_display(range_sin_profundidad) is None)


def test_duplicate_equipment_via_store():
    import tempfile
    from ansul.store import Store
    with tempfile.TemporaryDirectory() as tmp:
        store = Store(path=f'{tmp}/db.json')
        store.load()
        p = store.add_project('Proyecto de prueba')
        k = store.add_kitchen(p['id'], 'Sistema de prueba')
        item = store.add_equipment(p['id'], k['id'], {
            'category': 'wok', 'brand': 'Marca', 'model': 'Modelo X',
            'input': {'diam': '20', 'depth': '5'}, 'result': {'nozzles': [{'code': '1N', 'qty': 1}], 'flowNumber': 1}})
        dup = store.duplicate_equipment(p['id'], k['id'], item['id'])
        check('duplicate_equipment crea un nuevo id', dup['id'] != item['id'])
        check('duplicate_equipment conserva la categoría', dup['category'] == 'wok')
        k2 = store.get_kitchen(p['id'], k['id'])
        check('duplicate_equipment agrega un segundo renglón', len(k2['equipment']) == 2)


def test_duplicate_kitchen_via_store():
    import tempfile
    from ansul.store import Store
    with tempfile.TemporaryDirectory() as tmp:
        store = Store(path=f'{tmp}/db.json')
        store.load()
        p = store.add_project('Proyecto de prueba')
        k = store.add_kitchen(p['id'], 'Sistema original')
        store.add_equipment(p['id'], k['id'], {
            'category': 'wok', 'brand': 'Marca', 'model': 'Modelo X',
            'input': {'diam': '20', 'depth': '5'}, 'result': {'nozzles': [{'code': '1N', 'qty': 1}], 'flowNumber': 1}})
        store.set_kitchen_tank_override(p['id'], k['id'], {'enabled': True, 'tanks': [3]})
        dup = store.duplicate_kitchen(p['id'], k['id'])
        check('duplicate_kitchen crea un nuevo id de sistema', dup['id'] != k['id'])
        check('duplicate_kitchen agrega "(copia)" al nombre', dup['name'] == 'Sistema original (copia)')
        check('duplicate_kitchen copia los riesgos/equipos', len(dup['equipment']) == 1)
        check('duplicate_kitchen copia con nuevo id de equipo',
              dup['equipment'][0]['id'] != store.get_kitchen(p['id'], k['id'])['equipment'][0]['id'])
        check('duplicate_kitchen copia el override de tanques', dup.get('tankOverride', {}).get('enabled') is True)
        p2 = store.get_project(p['id'])
        check('duplicate_kitchen agrega un segundo sistema al proyecto', len(p2['kitchens']) == 2)


def test_kitchen_and_project_summary():
    kitchen = {'equipment': [
        {'result': {'nozzles': [{'code': '290', 'qty': 1}], 'flowNumber': 2}},
        {'result': {'nozzles': [{'code': '1N', 'qty': 1}], 'flowNumber': 1}},
    ]}
    s = E.kitchen_summary(kitchen)
    check('Resumen de sistema: flow total = 3', s['totalFlow'] == 3)
    check('Resumen de sistema: 1 tanque de 1.5 gal', s['tanks']['tanks'] == [1.5])

    project = {'kitchens': [kitchen, kitchen]}
    ps = E.project_summary(project)
    check('Resumen de proyecto: 2 tanques totales', ps['totalTanks'] == 2)
    check('Resumen de proyecto: boquilla 290 x2 en total', ps['nozzleTotals']['290'] == 2)
    check('Resumen de proyecto: capacidad total de flujo = 6', ps['totalFlow'] == 6)


def test_fits_long_side():
    # Regla "lado mayor + área" del Nozzle Application Chart (Manual R-102,
    # page 4-29 a 4-31). Estufa de 24 x 30 in: lado mayor 30, área 720 in^2.
    check('24x30 vs 1N alta (32 / 384) -> no cabe por área',
          E.fits_long_side_area(24, 30, 32, 384) is False)
    check('24x30 vs 245 alta (28 / 672) -> no cabe (lado y area)',
          E.fits_long_side_area(24, 30, 28, 672) is False)
    check('24x30 vs 260 media (32 / 768) -> si cabe',
          E.fits_long_side_area(24, 30, 32, 768) is True)
    # Tolerancia de redondeo: un error diminuto en el limite de sí debe caber...
    check('Lado 32 + error de redondeo -> sí cabe',
          E.fits_long_side_area(24, 32 + 1e-12, 32, 768) is True)
    # Un exceso real NO es aceptable.
    check('Lado 32.5 (exceso real) -> no cabe',
          E.fits_long_side_area(24, 32.5, 32, 768) is False)


def test_modules_field_is_optional():
    # El campo "Número de módulos (opcional)" no debe mostrar asterisco
    # de obligatorio en ninguna categoría (form_widgets usa 'required').
    for categoria, definicion in CD.CATEGORY_DEFS.items():
        for valores in ({}, {'hasDripboard': True}):
            for campo in definicion['fields'](valores):
                if campo['key'] == 'modules':
                    check(f'{categoria}: campo módulos no obligatorio',
                          campo.get('required', True) is False )


def test_load_corrupt_json_keeps_backups():
    # Un ansulcalc_db.json dañado NO debe perderse: load() debe apartarlo
    # con otro nombre antes de que cualquier save() escriba un archivo nuevo.
    import glob
    import tempfile
    from ansul.store import Store
    with tempfile.TemporaryDirectory() as tmp:
        ruta = f'{tmp}/db.json'
        danado = '{"projects": [{"name": "Hotel'
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(danado)

        store = Store(path=ruta)
        store.load()
        store.add_project('Proyecto nuevo')

        respaldos = glob.glob(f'{tmp}/db.corrupt-*.json')
        check('JSON dañado -> se aparta una copia', len(respaldos) == 1)
        with open(respaldos[0], encoding='utf-8') as f:
            check('La copia conserva el contenido original', f.read() == danado)
        check('Store registra dónde quedó la copia', str(store.corrupt_backup) == respaldos[0])


def test_load_valid_json_returns_database():
    import json
    import tempfile
    from ansul.store import Store
    with tempfile.TemporaryDirectory() as tmp:
        ruta = f'{tmp}/db.json'
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump({'projects': [{'name': 'Hotel', 'kitchens': []}]}, f)

        store = Store(path=ruta)
        datos = store.load()
        check('load() regresa los datos', datos is not None)
        check('load() conserva el proyecto guardado', datos['projects'][0]['name'] == 'Hotel')
        check('load() agrega customCatalog si falta', 'customCatalog' in datos)
        check('Archivo sano -> no hay respaldo corrupto', store.corrupt_backup is None)


def test_salamander_orientation_manual():
    # Manual R-102 (2017, rev. 13) pág. 4-24: límites de la cámara interna.
    #   1N cenital: 16 in de fondo x 29 in de ancho
    #   1F cenital y 1N local: 15 in de fondo x 31 in de ancho
    # En el formulario: 'length' = fondo (de frente a fondo), 'width' = ancho (de lado a lado).
    compute = CD.CATEGORY_DEFS['salamander']['compute']

    c = compute({'length': '16', 'width': '29'})
    ids = [m['id'] for m in c['matches']]
    check('Salamandra 16 fondo x 29 ancho -> admite 1N cenital', 'overhead1N' in ids)

    c = compute({'length': '29', 'width': '16'})
    check('Salamandra 29 fondo x 16 ancho -> ninguna opción', c['ok'] is False)

    c = compute({'length': '15', 'width': '31'})
    ids = [m['id'] for m in c['matches']]
    check('Salamandra 15 fondo x 31 ancho -> 1F y 1N local', set(ids) == {'overhead1F', 'local1N'})


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_') and callable(v)]
    for t in tests:
        t()
    print(f'\n{len(tests)} pruebas pasaron correctamente.')


if __name__ == '__main__':
    run_all()
