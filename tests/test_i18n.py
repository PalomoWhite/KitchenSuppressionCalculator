# -*- coding: utf-8 -*-
"""
Pruebas de idioma (español / inglés) y configuración.

Ejecutar:  python -m tests.test_i18n      (o todas:  python -m tests)
"""
import ast
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ansul.i18n_en import EN  # noqa: E402

SPANISH_HINT = re.compile(r'[áéíóúñ¿¡]|\b(de|del|la|el|los|las|con|por|para|sin|una)\b', re.I)


def check(label, cond):
    status = 'OK  ' if cond else 'FAIL'
    print(f'[{status}] {label}')
    if not cond:
        raise AssertionError(label)


def _templates():
    """Todos los textos que el código pasa a tr()."""
    out = {}
    files = glob.glob(os.path.join(ROOT, 'ansul', '**', '*.py'), recursive=True) + [os.path.join(ROOT, 'main.py')]
    for f in files:
        tree = ast.parse(open(f, encoding='utf-8').read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'tr' and n.args:
                a = n.args[0]
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    out.setdefault(a.value, f'{os.path.relpath(f, ROOT)}:{n.lineno}')
    return out


def _run_en(code, db_path):
    env = dict(os.environ, ANSULCALC_LANG='en', ANSULCALC_DB=db_path, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=env, capture_output=True, text=True,
                       encoding='utf-8')
    if r.returncode != 0:
        print(r.stderr)
    return r.stdout.strip()


def test_every_spanish_text_has_translation():
    missing = [(t, where) for t, where in _templates().items() if t not in EN and SPANISH_HINT.search(t)]
    for t, where in missing[:10]:
        print('   falta traducción:', where, repr(t)[:80])
    check('Todo texto en español que pasa por tr() tiene su traducción al inglés', not missing)


def test_placeholders_match():
    ph = lambda s: sorted(re.findall(r'\{[^{}]*\}', s))  # noqa: E731
    bad = [k for k, v in EN.items() if ph(k) != ph(v)]
    check('Las traducciones conservan los mismos {0}, {1}… que el texto en español', not bad)


def test_spanish_is_default_in_tests():
    from ansul import i18n
    from ansul.i18n import tr
    check('Las pruebas corren en español', i18n.language() == 'es' and tr('Nuevo proyecto…') == 'Nuevo proyecto…')


def test_english_results_and_labels():
    with tempfile.TemporaryDirectory() as tmp:
        out = _run_en(
            'import json\n'
            'from ansul.systems import get\n'
            'from ansul.systems.buckeye_bfr import engine as BE\n'
            'from ansul import category_defs as CD\n'
            'c = CD.CATEGORY_DEFS["fryer"]["compute"]({"frypotD": "14", "frypotL": "15"})\n'
            'r = CD.CATEGORY_DEFS["fryer"]["result_from_choice"](c, 0)\n'
            'p = BE.calc_plenum("single", 16)\n'
            'print(json.dumps({"label": get("buckeye_bfr").category_labels["fryer"], '
            '"ansul": get(None).category_labels["range"], "detail": r["detail"], "plenum": p["detail"], '
            '"flow": get("buckeye_bfr").flow_label}))',
            os.path.join(tmp, 'db.json'))
        d = json.loads(out)
        check('Inglés: nombre de categoría Buckeye', d['label'] == 'Deep Fat Fryer / Freidora')
        check('Inglés: nombre de categoría ANSUL', d['ansul'] == 'Range / Estufa')
        check('Inglés: detalle de pleno Buckeye en inglés', 'equal sections of 8 ft' in d['plenum']
              and 'Placement:' in d['plenum'])
        check('Inglés: sin palabras en español en el detalle de freidora ANSUL',
              not re.search(r'\b(modularizado|grupo|zonas)\b', d['detail']))


def test_saved_results_are_retranslated_without_changing_nozzles():
    from ansul.store import Store
    from ansul import systems
    from ansul.systems.buckeye_bfr import category_defs as BC
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, 'db.json')
        st = Store(path=db)
        st.load()
        p = st.add_project('Prueba', 'buckeye_bfr')
        k = st.add_kitchen(p['id'], 'Sistema 1')
        calc = BC.CATEGORY_DEFS['range']['compute']({'width': '24', 'depth': '24'})
        res = BC.CATEGORY_DEFS['range']['result_from_choice'](calc, 1)
        st.add_equipment(p['id'], k['id'], {'category': 'range', 'input': {'width': '24', 'depth': '24'},
                                            'chosenIdx': 1, 'result': res})
        before = json.load(open(db, encoding='utf-8'))
        _run_en('from ansul.store import Store\nimport os\nStore(path=os.environ["ANSULCALC_DB"]).load()', db)
        after = json.load(open(db, encoding='utf-8'))
        r0 = before['projects'][0]['kitchens'][0]['equipment'][0]['result']
        r1 = after['projects'][0]['kitchens'][0]['equipment'][0]['result']
        check('Al abrir en inglés, el detalle guardado se traduce', r1['detail'] != r0['detail']
              and 'Placement:' in r1['detail'])
        check('…y las boquillas y flow points NO cambian', r1['nozzles'] == r0['nozzles']
              and r1['flowNumber'] == r0['flowNumber'])
        check('…y se registra el idioma de los resultados', after.get('resultsLang') == 'en')
        # De regreso a español
        st2 = Store(path=db)
        st2.load()
        r2 = st2.data['projects'][0]['kitchens'][0]['equipment'][0]['result']
        check('Al volver a español, el detalle queda igual que el original', r2['detail'] == r0['detail'])
        check('El registro en sistemas sigue funcionando', systems.for_project(st2.data['projects'][0]).key == 'buckeye_bfr')


def test_settings_roundtrip():
    from ansul import settings
    with tempfile.TemporaryDirectory() as tmp:
        old = os.environ.get('ANSULCALC_DB')
        os.environ['ANSULCALC_DB'] = os.path.join(tmp, 'db.json')
        try:
            check('Configuración de fábrica: español y tema claro', settings.load() == {'language': 'es', 'theme': 'light'})
            settings.save(language='en', theme='dark')
            check('Se guarda idioma y tema', settings.load() == {'language': 'en', 'theme': 'dark'})
            check('settings.json queda junto a la base de datos',
                  os.path.exists(os.path.join(tmp, 'settings.json')))
            with open(os.path.join(tmp, 'settings.json'), 'w') as f:
                f.write('{dañado')
            check('Archivo dañado -> valores de fábrica (no truena)', settings.load()['language'] == 'es')
            try:
                settings.save(language='fr')
                ok = True
            except ValueError:
                ok = False
            check('Idioma no soportado -> error', ok is False)
        finally:
            if old is None:
                os.environ.pop('ANSULCALC_DB', None)
            else:
                os.environ['ANSULCALC_DB'] = old


def test_data_folder_keeps_old_name():
    from pathlib import Path
    from ansul import settings
    with tempfile.TemporaryDirectory() as home:
        docs = Path(home) / 'Documents'
        docs.mkdir()
        check('Instalación nueva: carpeta con el nombre nuevo',
              settings.default_data_dir(home) == docs / 'KitchenSuppressionCalculator')
        (docs / 'AnsulFlowCalculator').mkdir()
        check('Si ya hay proyectos en la carpeta del nombre anterior, se sigue usando esa',
              settings.default_data_dir(home) == docs / 'AnsulFlowCalculator')
        (docs / 'KitchenSuppressionCalculator').mkdir()
        check('Si ya existe la carpeta nueva, se usa la nueva',
              settings.default_data_dir(home) == docs / 'KitchenSuppressionCalculator')


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_') and callable(v)]
    for t in tests:
        t()
    print(f'\n{len(tests)} pruebas de idioma y configuración pasaron correctamente.')


if __name__ == '__main__':
    run_all()
