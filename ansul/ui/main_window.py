# -*- coding: utf-8 -*-
"""
Ventana principal — equivalente a renderHome/renderProjectView/
renderKitchenView de AnsulCalc.html: un árbol de Proyectos > Sistemas
(antes "Cocinas") a la izquierda y, a la derecha, el detalle de lo
seleccionado (riesgos, resumen de materiales, generación de reportes PDF).
"""
import os
import sys
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget,
                                QTreeWidgetItem, QStackedWidget, QLabel, QPushButton, QTableWidget,
                                QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QLineEdit,
                                QFormLayout, QGroupBox, QFileDialog, QMenu, QAbstractItemView, QCheckBox)

from .. import data as D
from .. import engine as E
from .. import report
from ..store import Store, today_iso
from ..category_defs import category_display_label, dimensions_display, depth_display
from .equipment_dialog import EquipmentDialog
from .catalog_dialog import CatalogManagerDialog
from .reference_dialog import ReferenceDialog
from .unit_converter_dialog import UnitConverterDialog

APP_TITLE = 'Ansul Flow Calculator — Sistema ANSUL(R) R-102'
DISCLAIMER_SHORT = ('Esta herramienta es una ayuda de diseño preliminar basada en el manual ANSUL(R) R-102. '
                     'El diseño final debe ser verificado y sellado por un diseñador certificado ANSUL R-102, '
                     'conforme a NFPA 17A y los códigos locales aplicables.')

ROLE_PROJECT = 'project'
ROLE_KITCHEN = 'kitchen'


class MainWindow(QMainWindow):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 760)

        self._build_menu()
        self._build_ui()
        self._refresh_tree()

    # ------------------------------------------------------------------
    # Menú
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = self.menuBar()

        m_file = menubar.addMenu('&Archivo')
        act_new_project = QAction('Nuevo proyecto…', self)
        act_new_project.triggered.connect(self._add_project)
        m_file.addAction(act_new_project)
        m_file.addSeparator()
        act_backup = QAction('Respaldar datos…', self)
        act_backup.triggered.connect(self._backup_data)
        m_file.addAction(act_backup)
        act_restore = QAction('Restaurar datos…', self)
        act_restore.triggered.connect(self._restore_data)
        m_file.addAction(act_restore)
        m_file.addSeparator()
        act_quit = QAction('Salir', self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_catalog = menubar.addMenu('&Catálogo')
        act_manage_catalog = QAction('Administrar mi catálogo…', self)
        act_manage_catalog.triggered.connect(self._open_catalog_manager)
        m_catalog.addAction(act_manage_catalog)

        m_ref = menubar.addMenu('&Referencia')
        act_piping = QAction('Requisitos de tubería / boquillas…', self)
        act_piping.triggered.connect(self._open_reference)
        m_ref.addAction(act_piping)

        m_tools = menubar.addMenu('&Herramientas')
        act_units = QAction('Convertidor pies ↔ metros…', self)
        act_units.triggered.connect(self._open_unit_converter)
        m_tools.addAction(act_units)

        m_help = menubar.addMenu('&Ayuda')
        act_about = QAction('Acerca de…', self)
        act_about.triggered.connect(self._show_about)
        m_help.addAction(act_about)

    # ------------------------------------------------------------------
    # UI general
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter)

        # ---- Panel izquierdo: árbol de proyectos/sistemas ----
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Proyectos y sistemas')
        self.tree.currentItemChanged.connect(self._on_tree_selection_changed)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_tree_context_menu)
        left_layout.addWidget(self.tree)

        tree_btn_row = QHBoxLayout()
        btn_add_project = QPushButton('+ Proyecto')
        btn_add_project.clicked.connect(self._add_project)
        self.btn_add_kitchen = QPushButton('+ Sistema')
        self.btn_add_kitchen.clicked.connect(self._add_kitchen)
        self.btn_add_kitchen.setEnabled(False)
        self.btn_add_kitchen.setToolTip('Primero crea un proyecto.')
        tree_btn_row.addWidget(btn_add_project)
        tree_btn_row.addWidget(self.btn_add_kitchen)
        left_layout.addLayout(tree_btn_row)
        splitter.addWidget(left)

        # ---- Panel derecho: detalle ----
        self.stack = QStackedWidget()
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 880])

        self.page_empty = self._build_empty_page()
        self.page_project = self._build_project_page()
        self.page_kitchen = self._build_kitchen_page()
        self.stack.addWidget(self.page_empty)
        self.stack.addWidget(self.page_project)
        self.stack.addWidget(self.page_kitchen)
        self.stack.setCurrentWidget(self.page_empty)

        footer = QLabel(DISCLAIMER_SHORT)
        footer.setWordWrap(True)
        footer.setStyleSheet('color:#777; font-size:11px; padding:6px 10px;')
        outer.addWidget(footer)

    def _build_empty_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addStretch()
        lbl = QLabel('Selecciona un proyecto o sistema a la izquierda, o crea un proyecto nuevo para comenzar.')
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet('color:#888; font-size:14px;')
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    # ------------------------------------------------------------------
    # Página de proyecto
    # ------------------------------------------------------------------
    def _build_project_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        header_row = QHBoxLayout()
        self.project_title_label = QLabel()
        self.project_title_label.setStyleSheet('font-size:18px; font-weight:bold;')
        header_row.addWidget(self.project_title_label)
        header_row.addStretch()
        btn_rename = QPushButton('Renombrar proyecto')
        btn_rename.clicked.connect(self._rename_current_project)
        btn_delete = QPushButton('Eliminar proyecto')
        btn_delete.clicked.connect(self._delete_current_project)
        header_row.addWidget(btn_rename)
        header_row.addWidget(btn_delete)
        layout.addLayout(header_row)

        quote_row = QHBoxLayout()
        quote_row.addWidget(QLabel('No. de cotización:'))
        self.project_quote_edit = QLineEdit()
        self.project_quote_edit.setPlaceholderText('Consecutivo de cotización (opcional)')
        self.project_quote_edit.editingFinished.connect(self._save_project_quote_number)
        quote_row.addWidget(self.project_quote_edit)
        quote_row.addStretch()
        layout.addLayout(quote_row)

        layout.addWidget(QLabel('Sistemas de este proyecto:'))
        self.kitchens_table = QTableWidget(0, 4)
        self.kitchens_table.setHorizontalHeaderLabels(['Sistema', 'Riesgos', 'Flow number', 'Tanques'])
        self.kitchens_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.kitchens_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.kitchens_table.itemDoubleClicked.connect(self._open_kitchen_from_table)
        layout.addWidget(self.kitchens_table)

        btn_add_kitchen2 = QPushButton('+ Agregar sistema')
        btn_add_kitchen2.clicked.connect(self._add_kitchen)
        layout.addWidget(btn_add_kitchen2)

        summary_box = QGroupBox('Resumen general del proyecto (todos los sistemas)')
        sb_layout = QVBoxLayout(summary_box)
        self.project_summary_label = QLabel()
        self.project_summary_label.setWordWrap(True)
        sb_layout.addWidget(self.project_summary_label)
        self.project_nozzle_table = QTableWidget(0, 3)
        self.project_nozzle_table.setHorizontalHeaderLabels(['Boquilla', 'No. de parte', 'Cantidad'])
        self.project_nozzle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sb_layout.addWidget(self.project_nozzle_table)
        layout.addWidget(summary_box)

        report_row = QHBoxLayout()
        report_row.addWidget(QLabel('Responsable:'))
        self.project_responsible_edit = QLineEdit()
        report_row.addWidget(self.project_responsible_edit)
        report_row.addWidget(QLabel('Fecha:'))
        self.project_date_edit = QLineEdit(today_iso())
        report_row.addWidget(self.project_date_edit)
        self.project_pdf_btn = QPushButton('Generar PDF del proyecto…')
        self.project_pdf_btn.clicked.connect(self._generate_project_pdf)
        self.project_pdf_btn.setEnabled(False)
        self.project_pdf_btn.setToolTip('El proyecto necesita al menos un sistema con riesgos asignados.')
        report_row.addWidget(self.project_pdf_btn)
        layout.addLayout(report_row)

        return w

    # ------------------------------------------------------------------
    # Página de sistema (antes "cocina")
    # ------------------------------------------------------------------
    def _build_kitchen_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        header_row = QHBoxLayout()
        self.kitchen_title_label = QLabel()
        self.kitchen_title_label.setStyleSheet('font-size:18px; font-weight:bold;')
        header_row.addWidget(self.kitchen_title_label)
        header_row.addStretch()
        btn_rename = QPushButton('Renombrar sistema')
        btn_rename.clicked.connect(self._rename_current_kitchen)
        btn_duplicate = QPushButton('Duplicar sistema')
        btn_duplicate.clicked.connect(self._duplicate_current_kitchen)
        btn_delete = QPushButton('Eliminar sistema')
        btn_delete.clicked.connect(self._delete_current_kitchen)
        header_row.addWidget(btn_rename)
        header_row.addWidget(btn_duplicate)
        header_row.addWidget(btn_delete)
        layout.addLayout(header_row, 0)

        layout.addWidget(QLabel('Riesgos, ductos y plenos:'), 0)
        self.equipment_table = QTableWidget(0, 7)
        self.equipment_table.setHorizontalHeaderLabels(
            ['Tipo', 'Marca / Modelo', 'Largo x Ancho', 'Profundidad', 'Boquillas', 'Flow', 'Altura'])
        self.equipment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.equipment_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.equipment_table.itemDoubleClicked.connect(lambda _: self._edit_equipment())
        self.equipment_table.setMinimumHeight(220)
        layout.addWidget(self.equipment_table, 4)

        eq_btn_row = QHBoxLayout()
        btn_add_eq = QPushButton('+ Agregar riesgo')
        btn_add_eq.clicked.connect(self._add_equipment)
        btn_edit_eq = QPushButton('Editar riesgo')
        btn_edit_eq.clicked.connect(self._edit_equipment)
        btn_dup_eq = QPushButton('Duplicar riesgo')
        btn_dup_eq.clicked.connect(self._duplicate_equipment)
        btn_del_eq = QPushButton('Eliminar riesgo')
        btn_del_eq.clicked.connect(self._delete_equipment)
        eq_btn_row.addWidget(btn_add_eq)
        eq_btn_row.addWidget(btn_edit_eq)
        eq_btn_row.addWidget(btn_dup_eq)
        eq_btn_row.addWidget(btn_del_eq)
        layout.addLayout(eq_btn_row, 0)

        tank_box = QGroupBox('Galonaje / selección de tanques')
        tank_layout = QHBoxLayout(tank_box)
        self.tank_override_check = QCheckBox('Elegir tanques manualmente (en vez de automático)')
        self.tank_override_check.toggled.connect(self._on_tank_override_toggled)
        tank_layout.addWidget(self.tank_override_check)
        tank_layout.addWidget(QLabel('Tanques de 1.5 gal:'))
        self.tank_15_edit = QLineEdit('0')
        self.tank_15_edit.setFixedWidth(50)
        self.tank_15_edit.editingFinished.connect(self._save_tank_override)
        tank_layout.addWidget(self.tank_15_edit)
        tank_layout.addWidget(QLabel('Tanques de 3 gal:'))
        self.tank_3_edit = QLineEdit('0')
        self.tank_3_edit.setFixedWidth(50)
        self.tank_3_edit.editingFinished.connect(self._save_tank_override)
        tank_layout.addWidget(self.tank_3_edit)
        tank_layout.addStretch()
        layout.addWidget(tank_box, 0)

        summary_box = QGroupBox('Resumen de materiales de este sistema')
        sb_layout = QVBoxLayout(summary_box)
        self.kitchen_summary_label = QLabel()
        self.kitchen_summary_label.setWordWrap(True)
        sb_layout.addWidget(self.kitchen_summary_label)
        self.kitchen_note_label = QLabel()
        self.kitchen_note_label.setWordWrap(True)
        self.kitchen_note_label.setStyleSheet('color:#8a6d00; background:#fff8e1; padding:6px; border-radius:4px;')
        self.kitchen_note_label.setVisible(False)
        sb_layout.addWidget(self.kitchen_note_label)
        self.kitchen_nozzle_table = QTableWidget(0, 3)
        self.kitchen_nozzle_table.setHorizontalHeaderLabels(['Boquilla', 'No. de parte', 'Cantidad'])
        self.kitchen_nozzle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sb_layout.addWidget(self.kitchen_nozzle_table)
        layout.addWidget(summary_box, 2)

        report_row = QHBoxLayout()
        report_row.addWidget(QLabel('Responsable:'))
        self.kitchen_responsible_edit = QLineEdit()
        report_row.addWidget(self.kitchen_responsible_edit)
        report_row.addWidget(QLabel('Fecha:'))
        self.kitchen_date_edit = QLineEdit(today_iso())
        report_row.addWidget(self.kitchen_date_edit)
        self.kitchen_pdf_btn = QPushButton('Generar PDF de este sistema…')
        self.kitchen_pdf_btn.clicked.connect(self._generate_kitchen_pdf)
        self.kitchen_pdf_btn.setEnabled(False)
        self.kitchen_pdf_btn.setToolTip('El sistema necesita al menos un riesgo agregado.')
        report_row.addWidget(self.kitchen_pdf_btn)
        layout.addLayout(report_row, 0)

        return w

    # ------------------------------------------------------------------
    # Árbol: construcción y selección
    # ------------------------------------------------------------------
    def _refresh_tree(self, select_kind=None, select_pid=None, select_kid=None):
        self.btn_add_kitchen.setEnabled(bool(self.store.data['projects']))
        self.tree.blockSignals(True)
        self.tree.clear()
        select_item = None
        for p in self.store.data['projects']:
            p_item = QTreeWidgetItem([p['name']])
            p_item.setData(0, Qt.UserRole, (ROLE_PROJECT, p['id'], None))
            self.tree.addTopLevelItem(p_item)
            for k in p.get('kitchens', []):
                k_item = QTreeWidgetItem([k['name']])
                k_item.setData(0, Qt.UserRole, (ROLE_KITCHEN, p['id'], k['id']))
                p_item.addChild(k_item)
            p_item.setExpanded(True)
            if select_kind == ROLE_PROJECT and select_pid == p['id']:
                select_item = p_item
            elif select_kind == ROLE_KITCHEN and select_pid == p['id']:
                for i in range(p_item.childCount()):
                    child = p_item.child(i)
                    if child.data(0, Qt.UserRole)[2] == select_kid:
                        select_item = child
        self.tree.blockSignals(False)
        if select_item:
            self.tree.setCurrentItem(select_item)
        else:
            self._on_tree_selection_changed(self.tree.currentItem(), None)

    def _current_selection(self):
        item = self.tree.currentItem()
        if not item:
            return None
        return item.data(0, Qt.UserRole)

    def _on_tree_selection_changed(self, current, previous):
        if not current:
            self.stack.setCurrentWidget(self.page_empty)
            return
        role, pid, kid = current.data(0, Qt.UserRole)
        if role == ROLE_PROJECT:
            self._show_project(pid)
        elif role == ROLE_KITCHEN:
            self._show_kitchen(pid, kid)

    def _on_tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        menu = QMenu(self)
        if item:
            role, pid, kid = item.data(0, Qt.UserRole)
            if role == ROLE_PROJECT:
                menu.addAction('Renombrar proyecto', lambda: self._rename_project(pid))
                menu.addAction('Agregar sistema', lambda: self._add_kitchen(pid))
                menu.addAction('Eliminar proyecto', lambda: self._delete_project(pid))
            else:
                menu.addAction('Renombrar sistema', lambda: self._rename_kitchen(pid, kid))
                menu.addAction('Duplicar sistema', lambda: self._duplicate_kitchen(pid, kid))
                menu.addAction('Eliminar sistema', lambda: self._delete_kitchen(pid, kid))
        else:
            menu.addAction('Nuevo proyecto…', self._add_project)
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    # ------------------------------------------------------------------
    # Proyectos: CRUD
    # ------------------------------------------------------------------
    def _add_project(self):
        name, ok = QInputDialog.getText(self, 'Nuevo proyecto', 'Nombre del proyecto:')
        if ok and name.strip():
            p = self.store.add_project(name.strip())
            self._refresh_tree(select_kind=ROLE_PROJECT, select_pid=p['id'])

    def _rename_project(self, pid):
        p = self.store.get_project(pid)
        if not p:
            return
        name, ok = QInputDialog.getText(self, 'Renombrar proyecto', 'Nuevo nombre:', text=p['name'])
        if ok and name.strip():
            self.store.rename_project(pid, name.strip())
            self._refresh_tree(select_kind=ROLE_PROJECT, select_pid=pid)

    def _rename_current_project(self):
        sel = self._current_selection()
        if sel and sel[0] == ROLE_PROJECT:
            self._rename_project(sel[1])

    def _delete_project(self, pid):
        p = self.store.get_project(pid)
        if not p:
            return
        if QMessageBox.question(self, 'Confirmar', f'¿Eliminar el proyecto "{p["name"]}" y todos sus sistemas y riesgos?'
                                 ) == QMessageBox.Yes:
            self.store.delete_project(pid)
            self._refresh_tree()

    def _delete_current_project(self):
        sel = self._current_selection()
        if sel and sel[0] == ROLE_PROJECT:
            self._delete_project(sel[1])

    # ------------------------------------------------------------------
    # Sistemas (antes "cocinas"): CRUD
    # ------------------------------------------------------------------
    def _current_project_id_for_add_kitchen(self):
        sel = self._current_selection()
        if not sel:
            if self.store.data['projects']:
                return self.store.data['projects'][0]['id']
            QMessageBox.information(self, 'Sin proyecto', 'Primero crea o selecciona un proyecto.')
            return None
        return sel[1]

    def _add_kitchen(self, pid=None):
        pid = pid or self._current_project_id_for_add_kitchen()
        if not pid:
            return
        name, ok = QInputDialog.getText(self, 'Nuevo sistema', 'Nombre del sistema:')
        if ok and name.strip():
            k = self.store.add_kitchen(pid, name.strip())
            self._refresh_tree(select_kind=ROLE_KITCHEN, select_pid=pid, select_kid=k['id'])

    def _rename_kitchen(self, pid, kid):
        k = self.store.get_kitchen(pid, kid)
        if not k:
            return
        name, ok = QInputDialog.getText(self, 'Renombrar sistema', 'Nuevo nombre:', text=k['name'])
        if ok and name.strip():
            self.store.rename_kitchen(pid, kid, name.strip())
            self._refresh_tree(select_kind=ROLE_KITCHEN, select_pid=pid, select_kid=kid)

    def _rename_current_kitchen(self):
        sel = self._current_selection()
        if sel and sel[0] == ROLE_KITCHEN:
            self._rename_kitchen(sel[1], sel[2])

    def _duplicate_kitchen(self, pid, kid):
        new_kitchen = self.store.duplicate_kitchen(pid, kid)
        if new_kitchen:
            self._refresh_tree(select_kind=ROLE_KITCHEN, select_pid=pid, select_kid=new_kitchen['id'])

    def _duplicate_current_kitchen(self):
        sel = self._current_selection()
        if sel and sel[0] == ROLE_KITCHEN:
            self._duplicate_kitchen(sel[1], sel[2])

    def _delete_kitchen(self, pid, kid):
        k = self.store.get_kitchen(pid, kid)
        if not k:
            return
        if QMessageBox.question(self, 'Confirmar', f'¿Eliminar el sistema "{k["name"]}" y todos sus riesgos?'
                                 ) == QMessageBox.Yes:
            self.store.delete_kitchen(pid, kid)
            self._refresh_tree(select_kind=ROLE_PROJECT, select_pid=pid)

    def _delete_current_kitchen(self):
        sel = self._current_selection()
        if sel and sel[0] == ROLE_KITCHEN:
            self._delete_kitchen(sel[1], sel[2])

    def _open_kitchen_from_table(self, table_item):
        row = table_item.row()
        kid = self.kitchens_table.item(row, 0).data(Qt.UserRole)
        pid = self._current_selection()[1]
        self._refresh_tree(select_kind=ROLE_KITCHEN, select_pid=pid, select_kid=kid)

    # ------------------------------------------------------------------
    # Mostrar proyecto
    # ------------------------------------------------------------------
    def _show_project(self, pid):
        p = self.store.get_project(pid)
        if not p:
            self.stack.setCurrentWidget(self.page_empty)
            return
        self.stack.setCurrentWidget(self.page_project)
        self.project_title_label.setText(p['name'])
        self.project_quote_edit.setText(p.get('quoteNumber', ''))

        has_equipment = any(k.get('equipment') for k in p.get('kitchens', []))
        self.project_pdf_btn.setEnabled(has_equipment)

        self.kitchens_table.setRowCount(0)
        for k in p.get('kitchens', []):
            s = E.kitchen_summary(k)
            row = self.kitchens_table.rowCount()
            self.kitchens_table.insertRow(row)
            name_item = QTableWidgetItem(k['name'])
            name_item.setData(Qt.UserRole, k['id'])
            self.kitchens_table.setItem(row, 0, name_item)
            self.kitchens_table.setItem(row, 1, QTableWidgetItem(str(s['itemCount'])))
            self.kitchens_table.setItem(row, 2, QTableWidgetItem(E.fmt_num(s['totalFlow'])))
            tank_txt = f"{s['tanks']['tankCount']} ({E.fmt_num(s['tanks']['totalGallons'])} gal)" if s['tanks']['tankCount'] else '—'
            self.kitchens_table.setItem(row, 3, QTableWidgetItem(tank_txt))

        ps = E.project_summary(p)
        self.project_summary_label.setText(
            f"<b>Sistemas:</b> {len(p['kitchens'])} &nbsp;&nbsp; "
            f"<b>Capacidad total de flujo (flow number):</b> {E.fmt_num(ps['totalFlow'])} &nbsp;&nbsp; "
            f"<b>Tanques totales a instalar:</b> {ps['totalTanks']} &nbsp;&nbsp; "
            f"<b>Galonaje total de agente:</b> {E.fmt_num(ps['totalGallons'])} gal")
        self._fill_nozzle_table(self.project_nozzle_table, ps['nozzleTotals'])
        self.project_responsible_edit.setText(self.store.data.get('lastResponsible', ''))

    # ------------------------------------------------------------------
    # Mostrar sistema
    # ------------------------------------------------------------------
    def _show_kitchen(self, pid, kid):
        k = self.store.get_kitchen(pid, kid)
        if not k:
            self.stack.setCurrentWidget(self.page_empty)
            return
        self.stack.setCurrentWidget(self.page_kitchen)
        self.kitchen_title_label.setText(k['name'])
        self.kitchen_pdf_btn.setEnabled(bool(k.get('equipment')))

        override = k.get('tankOverride') or {}
        self.tank_override_check.blockSignals(True)
        self.tank_15_edit.blockSignals(True)
        self.tank_3_edit.blockSignals(True)
        self.tank_override_check.setChecked(bool(override.get('enabled')))
        tanks = override.get('tanks') or []
        self.tank_15_edit.setText(str(sum(1 for t in tanks if abs(t - 1.5) < 1e-6)))
        self.tank_3_edit.setText(str(sum(1 for t in tanks if abs(t - 3) < 1e-6)))
        self.tank_15_edit.setEnabled(bool(override.get('enabled')))
        self.tank_3_edit.setEnabled(bool(override.get('enabled')))
        self.tank_override_check.blockSignals(False)
        self.tank_15_edit.blockSignals(False)
        self.tank_3_edit.blockSignals(False)

        self.equipment_table.setRowCount(0)
        for item in k.get('equipment', []):
            r = item.get('result') or {}
            row = self.equipment_table.rowCount()
            self.equipment_table.insertRow(row)
            type_item = QTableWidgetItem(category_display_label(item))
            type_item.setData(Qt.UserRole, item['id'])
            self.equipment_table.setItem(row, 0, type_item)
            brand_model = ' '.join(x for x in [item.get('brand'), item.get('model')] if x) or '—'
            self.equipment_table.setItem(row, 1, QTableWidgetItem(brand_model))
            self.equipment_table.setItem(row, 2, QTableWidgetItem(dimensions_display(item) or '—'))
            self.equipment_table.setItem(row, 3, QTableWidgetItem(depth_display(item) or '—'))
            nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (r.get('nozzles') or [])) or '—'
            self.equipment_table.setItem(row, 4, QTableWidgetItem(nozz_txt))
            self.equipment_table.setItem(row, 5, QTableWidgetItem(E.fmt_num(r.get('flowNumber'))))
            self.equipment_table.setItem(row, 6, QTableWidgetItem(r.get('heightRange', '—')))

        s = E.kitchen_summary(k)
        tanks = s['tanks']
        tank_lines = []
        if tanks['tankCount']:
            counts = E.tank_counts(tanks['tanks'])
            for g in sorted(counts.keys(), reverse=True):
                tank_lines.append(f"Tanque de {g} gal × {counts[g]}")
        tank_txt = '<br>'.join(tank_lines) if tank_lines else 'Sin riesgos calculados todavía'
        tanks_label = 'Tanques (selección manual):' if tanks.get('manual') else 'Tanques:'
        self.kitchen_summary_label.setText(
            f"<b>Flow number total:</b> {E.fmt_num(s['totalFlow'])}<br>"
            f"<b>{tanks_label}</b><br>{tank_txt}<br>"
            f"<b>Galonaje total de agente:</b> {E.fmt_num(tanks.get('totalGallons'))} gal<br>"
            f"<b>Cartucho — opción N2:</b> {tanks.get('n2') or '—'}<br>"
            f"<b>Cartucho — opción CO2 (alternativa, no ambos):</b> {tanks.get('co2') or '—'}")
        if tanks.get('note'):
            self.kitchen_note_label.setText(tanks['note'])
            self.kitchen_note_label.setVisible(True)
        else:
            self.kitchen_note_label.setVisible(False)
        self._fill_nozzle_table(self.kitchen_nozzle_table, s['nozzleTotals'])
        self.kitchen_responsible_edit.setText(self.store.data.get('lastResponsible', ''))

    def _fill_nozzle_table(self, table, nozzle_totals):
        table.setRowCount(0)
        for code in sorted(nozzle_totals.keys()):
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(code))
            table.setItem(row, 1, QTableWidgetItem(D.NOZZLES.get(code, {}).get('partNo', '—')))
            table.setItem(row, 2, QTableWidgetItem(str(nozzle_totals[code])))

    # ------------------------------------------------------------------
    # Riesgos (equipos): CRUD
    # ------------------------------------------------------------------
    def _current_kitchen_ids(self):
        sel = self._current_selection()
        if not sel or sel[0] != ROLE_KITCHEN:
            return None, None
        return sel[1], sel[2]

    def _add_equipment(self):
        pid, kid = self._current_kitchen_ids()
        if not pid:
            return
        dlg = EquipmentDialog(self.store, parent=self)
        if dlg.exec() == EquipmentDialog.Accepted and dlg.result_item:
            self.store.add_equipment(pid, kid, dlg.result_item)
            self._show_kitchen(pid, kid)

    def _selected_equipment_id(self):
        row = self.equipment_table.currentRow()
        if row < 0:
            return None
        return self.equipment_table.item(row, 0).data(Qt.UserRole)

    def _edit_equipment(self):
        pid, kid = self._current_kitchen_ids()
        eid = self._selected_equipment_id()
        if not pid or not eid:
            return
        item = self.store.get_equipment(pid, kid, eid)
        dlg = EquipmentDialog(self.store, existing_item=item, parent=self)
        if dlg.exec() == EquipmentDialog.Accepted and dlg.result_item:
            self.store.update_equipment(pid, kid, eid, dlg.result_item)
            self._show_kitchen(pid, kid)

    def _delete_equipment(self):
        pid, kid = self._current_kitchen_ids()
        eid = self._selected_equipment_id()
        if not pid or not eid:
            return
        if QMessageBox.question(self, 'Confirmar', '¿Eliminar este riesgo?') == QMessageBox.Yes:
            self.store.delete_equipment(pid, kid, eid)
            self._show_kitchen(pid, kid)

    def _duplicate_equipment(self):
        pid, kid = self._current_kitchen_ids()
        eid = self._selected_equipment_id()
        if not pid or not eid:
            return
        if self.store.duplicate_equipment(pid, kid, eid):
            self._show_kitchen(pid, kid)

    # ------------------------------------------------------------------
    # Galonaje / selección manual de tanques
    # ------------------------------------------------------------------
    def _on_tank_override_toggled(self, checked):
        self.tank_15_edit.setEnabled(checked)
        self.tank_3_edit.setEnabled(checked)
        self._save_tank_override()

    def _save_tank_override(self):
        pid, kid = self._current_kitchen_ids()
        if not pid:
            return
        enabled = self.tank_override_check.isChecked()
        try:
            n15 = max(0, int(self.tank_15_edit.text() or 0))
        except ValueError:
            n15 = 0
        try:
            n3 = max(0, int(self.tank_3_edit.text() or 0))
        except ValueError:
            n3 = 0
        override = {'enabled': enabled, 'tanks': [3] * n3 + [1.5] * n15} if enabled else None
        self.store.set_kitchen_tank_override(pid, kid, override)
        self._show_kitchen(pid, kid)

    # ------------------------------------------------------------------
    # Reportes PDF
    # ------------------------------------------------------------------
    def _sync_responsible(self, text):
        self.store.data['lastResponsible'] = text
        self.store.save()

    def _save_project_quote_number(self):
        sel = self._current_selection()
        if not sel or sel[0] != ROLE_PROJECT:
            return
        self.store.set_project_quote_number(sel[1], self.project_quote_edit.text().strip())

    def _generate_kitchen_pdf(self):
        pid, kid = self._current_kitchen_ids()
        if not pid:
            return
        p = self.store.get_project(pid)
        k = self.store.get_kitchen(pid, kid)
        responsible = self.kitchen_responsible_edit.text().strip()
        date = self.kitchen_date_edit.text().strip() or today_iso()
        self._sync_responsible(responsible)
        default_name = f"AnsulFlowCalculator_{report.pdf_sanitize_filename(k['name'])}_{date}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar reporte PDF de sistema', default_name, 'PDF (*.pdf)')
        if not path:
            return
        try:
            report.build_kitchen_report_pdf(p, k, path, responsible=responsible, date=date,
                                             quote_number=p.get('quoteNumber', ''))
        except Exception as e:
            QMessageBox.critical(self, 'Error al generar PDF', str(e))
            return
        self._offer_open_file(path)

    def _generate_project_pdf(self):
        sel = self._current_selection()
        if not sel or sel[0] != ROLE_PROJECT:
            return
        pid = sel[1]
        p = self.store.get_project(pid)
        responsible = self.project_responsible_edit.text().strip()
        date = self.project_date_edit.text().strip() or today_iso()
        self._sync_responsible(responsible)
        default_name = f"AnsulFlowCalculator_{report.pdf_sanitize_filename(p['name'])}_{date}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar reporte PDF del proyecto', default_name, 'PDF (*.pdf)')
        if not path:
            return
        try:
            report.build_project_report_pdf(p, path, responsible=responsible, date=date,
                                             quote_number=p.get('quoteNumber', ''))
        except Exception as e:
            QMessageBox.critical(self, 'Error al generar PDF', str(e))
            return
        self._offer_open_file(path)

    def _offer_open_file(self, path):
        if QMessageBox.question(self, 'PDF generado', f'El reporte se guardó en:\n{path}\n\n¿Abrirlo ahora?'
                                 ) == QMessageBox.Yes:
            try:
                if sys.platform.startswith('win'):
                    os.startfile(path)  # noqa
                elif sys.platform == 'darwin':
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception:
                webbrowser.open(path)

    # ------------------------------------------------------------------
    # Respaldo / restauración
    # ------------------------------------------------------------------
    def _backup_data(self):
        default_name = f'AnsulFlowCalculator_respaldo_{today_iso()}.json'
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar respaldo de datos', default_name, 'JSON (*.json)')
        if not path:
            return
        try:
            self.store.export_backup(path)
            QMessageBox.information(self, 'Respaldo guardado', f'Se guardó el respaldo en:\n{path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error al respaldar', str(e))

    def _restore_data(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Restaurar respaldo de datos', '', 'JSON (*.json)')
        if not path:
            return
        if QMessageBox.question(self, 'Confirmar restauración',
                                 'Esto reemplazará todos los proyectos, sistemas y catálogo propio actuales '
                                 'con el contenido del respaldo. ¿Continuar?') != QMessageBox.Yes:
            return
        try:
            self.store.import_backup(path)
            self._refresh_tree()
            QMessageBox.information(self, 'Restauración completa', 'Los datos se restauraron correctamente.')
        except Exception as e:
            QMessageBox.critical(self, 'Error al restaurar', str(e))

    # ------------------------------------------------------------------
    # Catálogo / referencia / acerca de
    # ------------------------------------------------------------------
    def _open_catalog_manager(self):
        dlg = CatalogManagerDialog(self.store, parent=self)
        dlg.exec()

    def _open_reference(self):
        dlg = ReferenceDialog(parent=self)
        dlg.exec()

    def _open_unit_converter(self):
        dlg = UnitConverterDialog(parent=self)
        dlg.exec()

    def _show_about(self):
        QMessageBox.information(self, 'Acerca de Ansul Flow Calculator',
                                 'Ansul Flow Calculator\n\n'
                                 'Calculadora de apoyo para el diseño preliminar de sistemas de supresión '
                                 'ANSUL(R) R-102 para cocinas comerciales, basada en el manual ANSUL(R) R-102 '
                                 '(Part No. 418087) y la Hoja Resumen F-2015158-01_LAS.\n\n' + DISCLAIMER_SHORT)

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self.store.save()
        event.accept()
