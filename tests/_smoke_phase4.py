# -*- coding: utf-8 -*-
"""
Smoke test offscreen (no requiere pantalla) que ejercita de punta a punta
las funciones nuevas de la Fase 4: categoría Robata, estufa a 6 quemadores,
pleno en metros, duplicar riesgo/equipo, duplicar sistema, override manual
de tanques, consecutivo de cotización, botones deshabilitados, diagrama en
vivo, tema QSS, y generación de PDF con todo lo anterior.

No es parte de la suite de pytest (usa la GUI real, aunque en modo
offscreen) — se ejecuta a mano con: QT_QPA_PLATFORM=offscreen python3
tests/_smoke_phase4.py
"""
import os
import sys
import tempfile

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from ansul.store import Store
from ansul.ui.main_window import MainWindow
from ansul.ui.equipment_dialog import EquipmentDialog
from ansul.ui.style import STYLE_QSS
from ansul.ui.unit_converter_dialog import UnitConverterDialog
from ansul import report
from ansul import engine as E


def check(label, cond):
    status = 'OK  ' if cond else 'FAIL'
    print(f'[{status}] {label}')
    if not cond:
        raise AssertionError(label)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_QSS)

    tmpdir = tempfile.mkdtemp()
    store = Store(path=os.path.join(tmpdir, 'db.json'))
    store.load()
    win = MainWindow(store)

    # ---- Botones deshabilitados sin proyecto ----
    check('Sin proyectos: "+ Sistema" deshabilitado', win.btn_add_kitchen.isEnabled() is False)

    # ---- Crear proyecto ----
    p = store.add_project('Restaurante Demo')
    win._refresh_tree(select_kind='project', select_pid=p['id'])
    check('Con 1 proyecto: "+ Sistema" habilitado', win.btn_add_kitchen.isEnabled() is True)
    check('PDF de proyecto deshabilitado (sin sistemas/riesgos)', win.project_pdf_btn.isEnabled() is False)

    # ---- Consecutivo de cotización ----
    win.project_quote_edit.setText('COT-2026-001')
    win._save_project_quote_number()
    p2 = store.get_project(p['id'])
    check('Consecutivo de cotización se guarda en el proyecto', p2.get('quoteNumber') == 'COT-2026-001')

    # ---- Crear sistema (antes "cocina") ----
    k = store.add_kitchen(p['id'], 'Sistema Principal')
    win._refresh_tree(select_kind='kitchen', select_pid=p['id'], select_kid=k['id'])
    check('PDF de sistema deshabilitado (sin riesgos)', win.kitchen_pdf_btn.isEnabled() is False)

    # ---- Categoría Robata vía EquipmentDialog ----
    dlg = EquipmentDialog(store, parent=win)
    idx = dlg.category_combo.findData('robata')
    check('Categoría Robata existe en el combo', idx >= 0)
    dlg.category_combo.setCurrentIndex(idx)
    dlg.form._widgets['d1'].setText('15')
    dlg.form._widgets['d2'].setText('15')
    check('Robata (carbón por defecto) calcula un resultado con boquilla 1N',
          dlg.final_result and dlg.final_result['nozzles'][0]['code'] == '1N')
    # Diagrama en vivo debe reflejar las medidas capturadas
    check('Diagrama de Robata quedó en modo rectángulo', dlg.diagram._mode == 'rect')
    check('Diagrama de Robata usa las dimensiones capturadas', dlg.diagram._dims == (15.0, 15.0))

    # ---- Convertidor rápido integrado en "Agregar riesgo" (m<->ft, in<->cm) ----
    dlg.converter_m_ft.edit_a.setText('10')
    dlg.converter_m_ft.edit_a.textEdited.emit('10')
    check('Convertidor integrado: 10 m -> ~32.8 ft',
          abs(float(dlg.converter_m_ft.edit_b.text()) - 32.8084) < 0.01)
    dlg.converter_in_cm.edit_a.setText('10')
    dlg.converter_in_cm.edit_a.textEdited.emit('10')
    check('Convertidor integrado: 10 in -> 25.4 cm',
          abs(float(dlg.converter_in_cm.edit_b.text()) - 25.4) < 0.001)

    if dlg.final_result:
        store.add_equipment(p['id'], k['id'], {
            'category': dlg.category, 'brand': '', 'model': 'Robata de prueba',
            'input': dict(dlg.values), 'chosenIdx': dlg.chosen_idx, 'catalogRef': None,
            'result': dlg.final_result,
        })

    # ---- Categoría Estufa a 6 quemadores (modularización automática, sin
    #      restringir a una sola boquilla fija) ----
    dlg2 = EquipmentDialog(store, parent=win)
    idx2 = dlg2.category_combo.findData('range')
    dlg2.category_combo.setCurrentIndex(idx2)
    burners_widget = dlg2.form._widgets['burners']
    burners_idx = burners_widget.findData('6')
    burners_widget.setCurrentIndex(burners_idx)
    dlg2.form._widgets['d1'].setText('56')
    dlg2.form._widgets['d2'].setText('10')
    check('Estufa 6 quemadores sobredimensionada -> se modulariza automáticamente',
          dlg2.current_calc['ok'] is True and dlg2.current_calc['modules'] > 1)
    check('Estufa 6 quemadores modularizada -> ofrece varias boquillas/proximidades',
          len({m['nozzle'] for m in dlg2.current_calc['matches']}) > 1)
    if dlg2.final_result:
        store.add_equipment(p['id'], k['id'], {
            'category': dlg2.category, 'brand': '', 'model': 'Estufa 6Q de prueba',
            'input': dict(dlg2.values), 'chosenIdx': dlg2.chosen_idx, 'catalogRef': None,
            'result': dlg2.final_result,
        })

    # ---- Categoría Pleno en metros ----
    dlg3 = EquipmentDialog(store, parent=win)
    idx3 = dlg3.category_combo.findData('plenum')
    dlg3.category_combo.setCurrentIndex(idx3)
    kind_widget = dlg3.form._widgets['kind']
    kind_idx = kind_widget.findData('vertical1W')
    kind_widget.setCurrentIndex(kind_idx)
    dlg3.form._widgets['lengthM'].setText('2.44')
    dlg3.form._widgets['widthM'].setText('1')
    check('Pleno vertical en metros calcula resultado válido',
          dlg3.final_result is not None and 'm' in dlg3.final_result['detail'])
    if dlg3.final_result:
        eq_id = store.add_equipment(p['id'], k['id'], {
            'category': dlg3.category, 'brand': '', 'model': 'Pleno de prueba',
            'input': dict(dlg3.values), 'chosenIdx': dlg3.chosen_idx, 'catalogRef': None,
            'result': dlg3.final_result,
        })['id']

    # ---- Categoría Wok (tiene diámetro + profundidad, ambos relevantes) ----
    dlg4 = EquipmentDialog(store, parent=win)
    idx4 = dlg4.category_combo.findData('wok')
    dlg4.category_combo.setCurrentIndex(idx4)
    dlg4.form._widgets['diam'].setText('12')
    dlg4.form._widgets['depth'].setText('5')
    check('Wok 12x5 calcula un resultado válido', dlg4.final_result is not None)
    if dlg4.final_result:
        store.add_equipment(p['id'], k['id'], {
            'category': dlg4.category, 'brand': '', 'model': 'Wok de prueba',
            'input': dict(dlg4.values), 'chosenIdx': dlg4.chosen_idx, 'catalogRef': None,
            'result': dlg4.final_result,
        })

    win._show_kitchen(p['id'], k['id'])
    check('Tabla de riesgos: columna "Largo x Ancho" muestra las medidas del Robata (15 x 15 in)',
          win.equipment_table.item(0, 2).text() == '15 x 15 in')
    check('Tabla de riesgos: columna "Profundidad" vacía cuando no se capturó (Robata sin profundidad)',
          win.equipment_table.item(0, 3).text() == '—')
    wok_row = next(r for r in range(win.equipment_table.rowCount())
                   if win.equipment_table.item(r, 0).text().startswith('Wok'))
    check('Tabla de riesgos: Wok muestra "Ø12 in" en "Largo x Ancho"',
          win.equipment_table.item(wok_row, 2).text() == 'Ø12 in')
    check('Tabla de riesgos: Wok muestra "5 in" en "Profundidad" (por separado)',
          win.equipment_table.item(wok_row, 3).text() == '5 in')
    check('PDF de sistema habilitado (ya tiene riesgos)', win.kitchen_pdf_btn.isEnabled() is True)
    win._refresh_tree(select_kind='project', select_pid=p['id'])
    check('PDF de proyecto habilitado (sistema con riesgos)', win.project_pdf_btn.isEnabled() is True)

    # ---- Duplicar riesgo (antes "equipo") ----
    k_before = store.get_kitchen(p['id'], k['id'])
    n_before = len(k_before['equipment'])
    win._refresh_tree(select_kind='kitchen', select_pid=p['id'], select_kid=k['id'])
    win.equipment_table.setCurrentCell(0, 0)
    win._duplicate_equipment()
    k_after = store.get_kitchen(p['id'], k['id'])
    check('Duplicar riesgo agrega un renglón más', len(k_after['equipment']) == n_before + 1)

    # ---- Override manual de tanques ----
    win.tank_override_check.setChecked(True)
    win.tank_3_edit.setText('2')
    win.tank_15_edit.setText('0')
    win._save_tank_override()
    k_override = store.get_kitchen(p['id'], k['id'])
    check('Override de tanques se guarda en el sistema', k_override.get('tankOverride', {}).get('enabled') is True)
    check('Override de tanques -> [3, 3]', k_override['tankOverride']['tanks'] == [3, 3])

    # ---- Duplicar sistema (antes "cocina") ----
    kitchens_before = len(store.get_project(p['id'])['kitchens'])
    win._refresh_tree(select_kind='kitchen', select_pid=p['id'], select_kid=k['id'])
    win._duplicate_current_kitchen()
    kitchens_after = store.get_project(p['id'])['kitchens']
    check('Duplicar sistema agrega un sistema más', len(kitchens_after) == kitchens_before + 1)
    dup_kitchen = next(kk for kk in kitchens_after if kk['id'] != k['id'])
    check('Sistema duplicado copia el nombre + " (copia)"', dup_kitchen['name'] == 'Sistema Principal (copia)')
    check('Sistema duplicado copia los riesgos', len(dup_kitchen['equipment']) == len(k_override['equipment']))
    check('Sistema duplicado copia el override de tanques',
          dup_kitchen.get('tankOverride', {}).get('enabled') is True)
    # Devolver la selección al sistema original para el resto de la prueba
    win._refresh_tree(select_kind='kitchen', select_pid=p['id'], select_kid=k['id'])

    # ---- Convertidor de unidades ----
    conv = UnitConverterDialog(parent=win)
    conv.ft_edit.setText('10')
    conv._on_ft_changed('10')
    check('Convertidor 10 ft -> ~3.05 m', conv.m_edit.text() in ('3.05', '3.048'))

    # ---- Generar PDF de sistema y de proyecto con todo lo anterior ----
    kitchen_pdf = os.path.join(tmpdir, 'kitchen.pdf')
    report.build_kitchen_report_pdf(store.get_project(p['id']), store.get_kitchen(p['id'], k['id']),
                                     kitchen_pdf, responsible='Ing. Prueba', date='2026-08-28',
                                     quote_number='COT-2026-001')
    check('PDF de sistema generado', os.path.isfile(kitchen_pdf) and os.path.getsize(kitchen_pdf) > 1000)

    project_pdf = os.path.join(tmpdir, 'project.pdf')
    report.build_project_report_pdf(store.get_project(p['id']), project_pdf, responsible='Ing. Prueba',
                                     date='2026-08-28', quote_number='COT-2026-001')
    check('PDF de proyecto generado', os.path.isfile(project_pdf) and os.path.getsize(project_pdf) > 1000)
    ps_final = E.project_summary(store.get_project(p['id']))
    check('Capacidad total de flujo del proyecto es > 0 (incluye el sistema duplicado)', ps_final['totalFlow'] > 0)

    print('\nTodas las pruebas de humo de la Fase 4 pasaron correctamente.')
    print(f'PDFs de prueba en: {tmpdir}')


if __name__ == '__main__':
    main()
