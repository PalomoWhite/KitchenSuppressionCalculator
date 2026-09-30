# -*- coding: utf-8 -*-
"""
Prueba de humo de la versión Android (Kivy/KivyMD) — igual que
_smoke_phase4.py para la versión de escritorio (PySide6), NO es parte de
la suite automática de regresión (tests/test_engine.py), porque necesita
un entorno gráfico (aunque sea uno "de mentira").

Requiere Kivy/KivyMD instalados y, en un servidor sin pantalla, Xvfb:

    pip install kivy kivymd plyer
    SDL_VIDEODRIVER=dummy xvfb-run -a python tests/_smoke_android.py

Recorre el flujo completo de la app: crear proyecto -> crear sistema ->
agregar riesgo (probando los tres tipos de campo: number/select/toggle,
incluyendo un campo "reflow" que cambia la estructura del formulario) ->
guardar -> editar -> duplicar -> generar PDF del sistema.
"""
import os
import sys
import shutil
import tempfile
import traceback

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ANDROID_DIR = os.path.join(_ROOT, 'android')
sys.path.insert(0, _ANDROID_DIR)

_FAILURES = []


def check(label, cond):
    status = 'OK  ' if cond else 'FAIL'
    print(f'[{status}] {label}')
    if not cond:
        _FAILURES.append(label)


def main():
    tmp_home = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp_home, '.config'), exist_ok=True)
    os.environ['HOME'] = tmp_home
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    from kivy.clock import Clock
    from main import AnsulMobileApp  # noqa: E402  (import tras fijar HOME/estado de Kivy)

    app = AnsulMobileApp()

    def run_checks(_dt):
        try:
            check('Store inicia vacío', app.store.data['projects'] == [])

            project = app.store.add_project('Restaurante Demo')
            app.go_systems(project['id'])
            check('Navega a "systems"', app.sm.current == 'systems')

            kitchen = app.store.add_kitchen(project['id'], 'Cocina Principal')
            app.go_risks(kitchen['id'])
            check('Navega a "risks"', app.sm.current == 'risks')

            # --- Freidora: campos number + choice (elegir boquilla) ---
            app.go_risk_form(None)
            form = app.risk_form_screen
            check('Categoría por defecto = freidora', form.category == 'fryer')
            form.values['frypotD'] = '15'
            form.form._on_value_changed('frypotD', '15')
            form.values['frypotL'] = '14'
            form.form._on_value_changed('frypotL', '14')
            check('Freidora calcula resultado', form.final_result is not None)
            check('Aparecen opciones de boquilla', len(form.choice_box.children) > 1)
            form.brand_field.text = 'Frymaster'
            form.model_field.text = 'FPH155'
            form._on_save()
            check('Regresa a "risks" tras guardar', app.sm.current == 'risks')

            kitchen = app.store.get_kitchen(project['id'], kitchen['id'])
            check('Riesgo #1 guardado', len(kitchen['equipment']) == 1)
            check('Riesgo #1 tiene boquillas asignadas', len(kitchen['equipment'][0]['result']['nozzles']) > 0)

            eid = kitchen['equipment'][0]['id']
            app.go_risk_form(eid)
            check('Editar precarga los valores capturados', str(form.values.get('frypotD')) == '15')

            # --- Wok: dos campos number obligatorios, sin choice de boquilla múltiple real ---
            app.go_risk_form(None)
            form.category_spinner.text = 'Wok / Wok'
            check('Cambia categoría a Wok', form.category == 'wok')
            form.values['diam'] = '12'
            form.form._on_value_changed('diam', '12')
            form.values['depth'] = '5'
            form.form._on_value_changed('depth', '5')
            check('Wok calcula resultado', form.final_result is not None)
            form._on_save()

            # --- Ducto: campo 'toggle' con reflow (redondo/rectangular) ---
            app.go_risk_form(None)
            form.category_spinner.text = 'Ducto / Duct'
            check('Cambia categoría a Ducto', form.category == 'duct')
            form.values['round'] = True
            form._on_structure_changed()
            form.values['diameter'] = '10'
            form.form._on_value_changed('diameter', '10')
            check('Ducto redondo calcula resultado', form.final_result is not None)
            form._on_save()

            kitchen = app.store.get_kitchen(project['id'], kitchen['id'])
            check('3 riesgos guardados en total', len(kitchen['equipment']) == 3)

            # --- Lista de riesgos + resumen + PDF ---
            app.go_risks(kitchen['id'])
            app.risks_screen.refresh()
            check('La lista muestra tarjeta resumen + 3 riesgos', len(app.risks_screen.content_box.children) == 4)

            app.risks_screen._generate_pdf()
            reports_dir = os.path.join(app.user_data_dir, 'reportes')
            pdfs = os.listdir(reports_dir) if os.path.isdir(reports_dir) else []
            check('Se generó un PDF del sistema', len(pdfs) == 1)
            if pdfs:
                size = os.path.getsize(os.path.join(reports_dir, pdfs[0]))
                check(f'El PDF tiene contenido ({size} bytes)', size > 1000)

            # --- Duplicar sistema y proyecto persistido ---
            app.systems_screen.refresh()
            app.systems_screen._duplicate(kitchen['id'])
            project = app.store.get_project(project['id'])
            check('Duplicar sistema agrega un segundo sistema', len(project['kitchens']) == 2)

        except Exception:
            traceback.print_exc()
            _FAILURES.append('excepción no controlada — ver traceback arriba')
        finally:
            app.stop()

    Clock.schedule_once(run_checks, 0.5)
    app.run()
    shutil.rmtree(tmp_home, ignore_errors=True)

    print()
    if _FAILURES:
        print(f'{len(_FAILURES)} verificación(es) fallaron:')
        for f in _FAILURES:
            print(f'  - {f}')
        sys.exit(1)
    else:
        print('Todas las verificaciones de humo de la versión Android pasaron correctamente.')


if __name__ == '__main__':
    main()
