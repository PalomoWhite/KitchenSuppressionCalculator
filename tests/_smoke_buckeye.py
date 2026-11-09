# -*- coding: utf-8 -*-
"""
Prueba de humo de la interfaz con un proyecto Buckeye (offscreen, sin
pantalla): crear proyecto con marca, capturar riesgos con el formulario,
elegir combinación de cilindros, abrir la referencia y generar los PDF.

No es parte de la suite automática (necesita PySide6). Ejecutar:
    QT_QPA_PLATFORM=offscreen python tests/_smoke_buckeye.py
"""
import os
import sys
import tempfile

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from ansul import report, systems
from ansul.store import Store
from ansul.ui.main_window import MainWindow
from ansul.ui.equipment_dialog import EquipmentDialog
from ansul.ui.buckeye_reference_dialog import BuckeyeReferenceDialog
from ansul.ui.style import STYLE_QSS


def check(label, cond):
    print(f"[{'OK  ' if cond else 'FAIL'}] {label}")
    if not cond:
        raise AssertionError(label)


def _add(win, store, pid, kid, category, values, choice=0):
    bk = systems.get('buckeye_bfr')
    dlg = EquipmentDialog(store, parent=win, system=bk)
    dlg.category_combo.setCurrentIndex(list(bk.category_order).index(category))
    dlg.values.update(values)
    dlg._rebuild_form()
    dlg._recompute()
    if dlg.choice_group.isVisible():
        dlg.choice_list.setCurrentRow(choice)
    dlg._on_accept()
    check(f'{category}: el formulario produce un resultado', dlg.result_item is not None)
    store.add_equipment(pid, kid, dlg.result_item)
    return dlg


def main(out_dir=None):
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_QSS)
    tmp = out_dir or tempfile.mkdtemp()
    store = Store(path=os.path.join(tmp, 'db.json'))
    store.load()
    win = MainWindow(store)
    win.resize(1200, 860)

    p = store.add_project('Restaurante prueba Buckeye', 'buckeye_bfr')
    k = store.add_kitchen(p['id'], 'Campana principal')
    win._refresh_tree(select_kind='kitchen', select_pid=p['id'], select_kid=k['id'])

    dlg = _add(win, store, p['id'], k['id'], 'range', {'width': '24', 'depth': '24', 'backShelf': False})
    check('Estufa 24x24: la primera opción es N-1LP (1 FP)', dlg.result_item['result']['flowNumber'] == 1)
    check('El diálogo usa el título de la marca', 'Buckeye' in dlg.windowTitle())
    check('Buckeye no muestra el botón de catálogo ANSUL', not dlg.catalog_btn.isVisibleTo(dlg))
    dlg.resize(900, 760)
    dlg.show()
    app.processEvents()
    dlg.grab().save(os.path.join(tmp, 'dialogo_estufa.png'))
    dlg.close()

    _add(win, store, p['id'], k['id'], 'fryer', {'width': '36', 'depth': '24'})
    _add(win, store, p['id'], k['id'], 'griddle', {'width': '60', 'depth': '30'})
    _add(win, store, p['id'], k['id'], 'duct', {'sideA': '16', 'sideB': '8', 'qty': '1'})
    _add(win, store, p['id'], k['id'], 'plenum', {'kind': 'single', 'lengthM': '4', 'widthM': '1'})
    _add(win, store, p['id'], k['id'], 'wok', {'diam': '20'})

    win._show_kitchen(p['id'], k['id'])
    s = systems.get('buckeye_bfr').kitchen_summary(store.get_kitchen(p['id'], k['id']))
    # 1 (estufa) + 4 (freidora 2 × N-2HP) + 2 (plancha N-2LP) + 1 (ducto) + 2 (pleno 4 m = 13.1 ft) + 1 (wok)
    check('Total de flow points del sistema = 11', s['totalFlow'] == 11)
    check('Selector de cilindros visible y con opciones',
          win.cylinder_box.isVisibleTo(win) and win.cylinder_combo.count() > 1)
    check('Caja de tanques ANSUL oculta', not win.tank_box.isVisibleTo(win))
    check('Encabezado de tabla de boquillas con color', win.kitchen_nozzle_table.columnCount() == 4)

    win.cylinder_combo.setCurrentIndex(1)
    saved = store.get_kitchen(p['id'], k['id']).get('cylinderChoice')
    check('Elegir otra combinación la guarda en el sistema', bool(saved))
    win.show()
    app.processEvents()
    win.grab().save(os.path.join(tmp, 'sistema_buckeye.png'))

    win._refresh_tree(select_kind='project', select_pid=p['id'])
    app.processEvents()
    check('Proyecto con riesgos: botón "Cambiar marca" deshabilitado', not win.btn_change_brand.isEnabled())
    check('Árbol muestra la marca', '[Buckeye]' in win.tree.topLevelItem(0).text(0))
    win.grab().save(os.path.join(tmp, 'proyecto_buckeye.png'))

    ref = BuckeyeReferenceDialog(parent=win)
    ref.show()
    app.processEvents()
    ref.close()

    k_pdf = os.path.join(tmp, 'sistema_buckeye.pdf')
    p_pdf = os.path.join(tmp, 'proyecto_buckeye.pdf')
    report.build_kitchen_report_pdf(store.get_project(p['id']), store.get_kitchen(p['id'], k['id']), k_pdf,
                                    responsible='Prueba')
    report.build_project_report_pdf(store.get_project(p['id']), p_pdf, responsible='Prueba')
    check('PDF de sistema Buckeye generado', os.path.getsize(k_pdf) > 1000)
    check('PDF de proyecto Buckeye generado', os.path.getsize(p_pdf) > 1000)

    # Un proyecto ANSUL en el mismo archivo sigue funcionando igual.
    pa = store.add_project('Proyecto ANSUL', 'ansul_r102')
    ka = store.add_kitchen(pa['id'], 'Sistema 1')
    win._refresh_tree(select_kind='kitchen', select_pid=pa['id'], select_kid=ka['id'])
    check('Proyecto ANSUL: caja de tanques visible, cilindros oculto',
          win.tank_box.isVisibleTo(win) and not win.cylinder_box.isVisibleTo(win))

    print(f'\nPrueba de humo Buckeye OK. Archivos en: {tmp}')
    return tmp


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
