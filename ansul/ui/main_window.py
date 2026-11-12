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
                                QFormLayout, QGroupBox, QFileDialog, QMenu, QAbstractItemView, QCheckBox,
                                QComboBox)

from .. import engine as E
from .. import report
from .. import systems
from ..store import Store, today_iso
from .equipment_dialog import EquipmentDialog
from .catalog_dialog import CatalogManagerDialog
from .reference_dialog import ReferenceDialog
from .unit_converter_dialog import UnitConverterDialog
from ..i18n import tr
from .style import set_role

AUTHOR = 'Miguel Alejandro Gutiérrez Torres'
APP_TITLE = tr('Kitchen Suppression Calculator — ANSUL(R) R-102 / Buckeye Kitchen Mister')
DISCLAIMER_SHORT = systems.get(None).disclaimer_short

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

        m_file = menubar.addMenu(tr('&Archivo'))
        act_new_project = QAction(tr('Nuevo proyecto…'), self)
        act_new_project.triggered.connect(self._add_project)
        m_file.addAction(act_new_project)
        m_file.addSeparator()
        act_backup = QAction(tr('Respaldar datos…'), self)
        act_backup.triggered.connect(self._backup_data)
        m_file.addAction(act_backup)
        act_restore = QAction(tr('Restaurar datos…'), self)
        act_restore.triggered.connect(self._restore_data)
        m_file.addAction(act_restore)
        m_file.addSeparator()
        act_quit = QAction(tr('Salir'), self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_catalog = menubar.addMenu(tr('&Catálogo'))
        act_manage_catalog = QAction(tr('Administrar mi catálogo (ANSUL)…'), self)
        act_manage_catalog.triggered.connect(self._open_catalog_manager)
        m_catalog.addAction(act_manage_catalog)

        m_ref = menubar.addMenu(tr('&Referencia'))
        act_piping = QAction(tr('ANSUL R-102: tubería / boquillas…'), self)
        act_piping.triggered.connect(self._open_reference)
        m_ref.addAction(act_piping)
        act_buckeye = QAction(tr('Buckeye Kitchen Mister: boquillas, cilindros, coberturas y tubería…'), self)
        act_buckeye.triggered.connect(self._open_buckeye_reference)
        m_ref.addAction(act_buckeye)

        m_tools = menubar.addMenu(tr('&Herramientas'))
        act_units = QAction(tr('Convertidor pies ↔ metros…'), self)
        act_units.triggered.connect(self._open_unit_converter)
        m_tools.addAction(act_units)

        m_settings = menubar.addMenu(tr('&Configuración'))
        act_settings = QAction(tr('Idioma y tema…'), self)
        act_settings.triggered.connect(self._open_settings)
        m_settings.addAction(act_settings)

        m_help = menubar.addMenu(tr('&Ayuda'))
        act_about = QAction(tr('Acerca de…'), self)
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
        self.tree.setHeaderLabel(tr('Proyectos y sistemas'))
        self.tree.currentItemChanged.connect(self._on_tree_selection_changed)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_tree_context_menu)
        left_layout.addWidget(self.tree)

        tree_btn_row = QHBoxLayout()
        btn_add_project = QPushButton(tr('+ Proyecto'))
        btn_add_project.clicked.connect(self._add_project)
        self.btn_add_kitchen = QPushButton(tr('+ Sistema'))
        self.btn_add_kitchen.clicked.connect(self._add_kitchen)
        self.btn_add_kitchen.setEnabled(False)
        self.btn_add_kitchen.setToolTip(tr('Primero crea un proyecto.'))
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

        self.footer = QLabel(DISCLAIMER_SHORT)
        self.footer.setWordWrap(True)
        set_role(self.footer, 'footer')
        outer.addWidget(self.footer)

    def _build_empty_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addStretch()
        lbl = QLabel(tr('Selecciona un proyecto o sistema a la izquierda, o crea un proyecto nuevo para comenzar.'))
        lbl.setAlignment(Qt.AlignCenter)
        set_role(lbl, 'empty')
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
        set_role(self.project_title_label, 'title')
        header_row.addWidget(self.project_title_label)
        header_row.addStretch()
        btn_rename = QPushButton(tr('Renombrar proyecto'))
        btn_rename.clicked.connect(self._rename_current_project)
        btn_delete = QPushButton(tr('Eliminar proyecto'))
        btn_delete.clicked.connect(self._delete_current_project)
        header_row.addWidget(btn_rename)
        header_row.addWidget(btn_delete)
        layout.addLayout(header_row)

        brand_row = QHBoxLayout()
        self.project_brand_label = QLabel()
        set_role(self.project_brand_label, 'brand')
        brand_row.addWidget(self.project_brand_label)
        self.btn_change_brand = QPushButton(tr('Cambiar marca…'))
        self.btn_change_brand.clicked.connect(self._change_current_project_system)
        brand_row.addWidget(self.btn_change_brand)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        quote_row = QHBoxLayout()
        quote_row.addWidget(QLabel(tr('No. de cotización:')))
        self.project_quote_edit = QLineEdit()
        self.project_quote_edit.setPlaceholderText(tr('Consecutivo de cotización (opcional)'))
        self.project_quote_edit.editingFinished.connect(self._save_project_quote_number)
        quote_row.addWidget(self.project_quote_edit)
        quote_row.addStretch()
        layout.addLayout(quote_row)

        layout.addWidget(QLabel(tr('Sistemas de este proyecto:')))
        self.kitchens_table = QTableWidget(0, 4)
        self.kitchens_table.setHorizontalHeaderLabels([tr('Sistema'), tr('Riesgos'), tr('Flow number'), tr('Tanques')])
        self.kitchens_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.kitchens_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.kitchens_table.itemDoubleClicked.connect(self._open_kitchen_from_table)
        layout.addWidget(self.kitchens_table)

        btn_add_kitchen2 = QPushButton(tr('+ Agregar sistema'))
        btn_add_kitchen2.clicked.connect(self._add_kitchen)
        layout.addWidget(btn_add_kitchen2)

        summary_box = QGroupBox(tr('Resumen general del proyecto (todos los sistemas)'))
        sb_layout = QVBoxLayout(summary_box)
        self.project_summary_label = QLabel()
        self.project_summary_label.setWordWrap(True)
        sb_layout.addWidget(self.project_summary_label)
        self.project_nozzle_table = QTableWidget(0, 3)
        self.project_nozzle_table.setHorizontalHeaderLabels([tr('Boquilla'), tr('No. de parte'), tr('Cantidad')])
        self.project_nozzle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sb_layout.addWidget(self.project_nozzle_table)
        layout.addWidget(summary_box)

        report_row = QHBoxLayout()
        report_row.addWidget(QLabel(tr('Responsable:')))
        self.project_responsible_edit = QLineEdit()
        report_row.addWidget(self.project_responsible_edit)
        report_row.addWidget(QLabel(tr('Fecha:')))
        self.project_date_edit = QLineEdit(today_iso())
        report_row.addWidget(self.project_date_edit)
        self.project_pdf_btn = QPushButton(tr('Generar PDF del proyecto…'))
        self.project_pdf_btn.clicked.connect(self._generate_project_pdf)
        self.project_pdf_btn.setEnabled(False)
        self.project_pdf_btn.setToolTip(tr('El proyecto necesita al menos un sistema con riesgos asignados.'))
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
        set_role(self.kitchen_title_label, 'title')
        header_row.addWidget(self.kitchen_title_label)
        header_row.addStretch()
        btn_rename = QPushButton(tr('Renombrar sistema'))
        btn_rename.clicked.connect(self._rename_current_kitchen)
        btn_duplicate = QPushButton(tr('Duplicar sistema'))
        btn_duplicate.clicked.connect(self._duplicate_current_kitchen)
        btn_delete = QPushButton(tr('Eliminar sistema'))
        btn_delete.clicked.connect(self._delete_current_kitchen)
        header_row.addWidget(btn_rename)
        header_row.addWidget(btn_duplicate)
        header_row.addWidget(btn_delete)
        layout.addLayout(header_row, 0)

        layout.addWidget(QLabel(tr('Riesgos, ductos y plenos:')), 0)
        self.equipment_table = QTableWidget(0, 7)
        self.equipment_table.setHorizontalHeaderLabels(
            [tr('Tipo'), tr('Marca / Modelo'), tr('Largo x Ancho'), tr('Profundidad'), tr('Boquillas'), tr('Flow'), tr('Altura')])
        self.equipment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.equipment_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.equipment_table.itemDoubleClicked.connect(lambda _: self._edit_equipment())
        self.equipment_table.setMinimumHeight(220)
        layout.addWidget(self.equipment_table, 4)

        eq_btn_row = QHBoxLayout()
        btn_add_eq = QPushButton(tr('+ Agregar riesgo'))
        btn_add_eq.clicked.connect(self._add_equipment)
        btn_edit_eq = QPushButton(tr('Editar riesgo'))
        btn_edit_eq.clicked.connect(self._edit_equipment)
        btn_dup_eq = QPushButton(tr('Duplicar riesgo'))
        btn_dup_eq.clicked.connect(self._duplicate_equipment)
        btn_del_eq = QPushButton(tr('Eliminar riesgo'))
        btn_del_eq.clicked.connect(self._delete_equipment)
        eq_btn_row.addWidget(btn_add_eq)
        eq_btn_row.addWidget(btn_edit_eq)
        eq_btn_row.addWidget(btn_dup_eq)
        eq_btn_row.addWidget(btn_del_eq)
        layout.addLayout(eq_btn_row, 0)

        # Buckeye: selector de combinación de cilindros (todas las opciones mínimas).
        self.cylinder_box = QGroupBox(tr('Cilindros Buckeye — combinaciones posibles (elija una)'))
        cyl_layout = QHBoxLayout(self.cylinder_box)
        self.cylinder_combo = QComboBox()
        self.cylinder_combo.setMinimumWidth(380)
        self.cylinder_combo.currentIndexChanged.connect(self._on_cylinder_choice_changed)
        cyl_layout.addWidget(self.cylinder_combo)
        cyl_layout.addStretch()
        layout.addWidget(self.cylinder_box, 0)

        tank_box = QGroupBox(tr('Galonaje / selección de tanques'))
        self.tank_box = tank_box
        tank_layout = QHBoxLayout(tank_box)
        self.tank_override_check = QCheckBox(tr('Elegir tanques manualmente (en vez de automático)'))
        self.tank_override_check.toggled.connect(self._on_tank_override_toggled)
        tank_layout.addWidget(self.tank_override_check)
        tank_layout.addWidget(QLabel(tr('Tanques de 1.5 gal:')))
        self.tank_15_edit = QLineEdit('0')
        self.tank_15_edit.setFixedWidth(50)
        self.tank_15_edit.editingFinished.connect(self._save_tank_override)
        tank_layout.addWidget(self.tank_15_edit)
        tank_layout.addWidget(QLabel(tr('Tanques de 3 gal:')))
        self.tank_3_edit = QLineEdit('0')
        self.tank_3_edit.setFixedWidth(50)
        self.tank_3_edit.editingFinished.connect(self._save_tank_override)
        tank_layout.addWidget(self.tank_3_edit)
        tank_layout.addStretch()
        layout.addWidget(tank_box, 0)

        summary_box = QGroupBox(tr('Resumen de materiales de este sistema'))
        sb_layout = QVBoxLayout(summary_box)
        self.kitchen_summary_label = QLabel()
        self.kitchen_summary_label.setWordWrap(True)
        sb_layout.addWidget(self.kitchen_summary_label)
        self.kitchen_note_label = QLabel()
        self.kitchen_note_label.setWordWrap(True)
        set_role(self.kitchen_note_label, 'note')
        self.kitchen_note_label.setVisible(False)
        sb_layout.addWidget(self.kitchen_note_label)
        self.kitchen_nozzle_table = QTableWidget(0, 3)
        self.kitchen_nozzle_table.setHorizontalHeaderLabels([tr('Boquilla'), tr('No. de parte'), tr('Cantidad')])
        self.kitchen_nozzle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sb_layout.addWidget(self.kitchen_nozzle_table)
        layout.addWidget(summary_box, 2)

        report_row = QHBoxLayout()
        report_row.addWidget(QLabel(tr('Responsable:')))
        self.kitchen_responsible_edit = QLineEdit()
        report_row.addWidget(self.kitchen_responsible_edit)
        report_row.addWidget(QLabel(tr('Fecha:')))
        self.kitchen_date_edit = QLineEdit(today_iso())
        report_row.addWidget(self.kitchen_date_edit)
        self.kitchen_pdf_btn = QPushButton(tr('Generar PDF de este sistema…'))
        self.kitchen_pdf_btn.clicked.connect(self._generate_kitchen_pdf)
        self.kitchen_pdf_btn.setEnabled(False)
        self.kitchen_pdf_btn.setToolTip(tr('El sistema necesita al menos un riesgo agregado.'))
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
            p_item = QTreeWidgetItem([f"{p['name']}  [{systems.for_project(p).short}]"])
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
                menu.addAction(tr('Renombrar proyecto'), lambda: self._rename_project(pid))
                menu.addAction(tr('Agregar sistema'), lambda: self._add_kitchen(pid))
                menu.addAction(tr('Eliminar proyecto'), lambda: self._delete_project(pid))
            else:
                menu.addAction(tr('Renombrar sistema'), lambda: self._rename_kitchen(pid, kid))
                menu.addAction(tr('Duplicar sistema'), lambda: self._duplicate_kitchen(pid, kid))
                menu.addAction(tr('Eliminar sistema'), lambda: self._delete_kitchen(pid, kid))
        else:
            menu.addAction(tr('Nuevo proyecto…'), self._add_project)
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    # ------------------------------------------------------------------
    # Proyectos: CRUD
    # ------------------------------------------------------------------
    def _ask_system(self, title, current=None):
        """Pregunta la marca del proyecto. Regresa la clave o None si se canceló."""
        labels = [label for _key, label in systems.CHOICES]
        keys = [key for key, _label in systems.CHOICES]
        idx = keys.index(current) if current in keys else 0
        label, ok = QInputDialog.getItem(self, title, tr('Marca del sistema de supresión:\n(todos los sistemas del proyecto serán de esta marca)'),
                                         labels, idx, False)
        if not ok:
            return None
        return keys[labels.index(label)]

    def _add_project(self):
        system = self._ask_system(tr('Nuevo proyecto'))
        if not system:
            return
        name, ok = QInputDialog.getText(self, tr('Nuevo proyecto'), tr('Nombre del proyecto:'))
        if ok and name.strip():
            p = self.store.add_project(name.strip(), system)
            self._refresh_tree(select_kind=ROLE_PROJECT, select_pid=p['id'])

    def _change_current_project_system(self):
        sel = self._current_selection()
        if not sel or sel[0] != ROLE_PROJECT:
            return
        p = self.store.get_project(sel[1])
        if not p:
            return
        if self.store.project_has_equipment(p):
            QMessageBox.information(self, tr('Cambiar marca'),
                                    tr('Este proyecto ya tiene riesgos capturados: no se puede cambiar la marca (no se permiten '
                                       'proyectos mixtos). Cree un proyecto nuevo con la otra marca.'))
            return
        system = self._ask_system(tr('Cambiar marca'), p.get('system'))
        if system and system != p.get('system'):
            self.store.set_project_system(p['id'], system)
            self._refresh_tree(select_kind=ROLE_PROJECT, select_pid=p['id'])

    def _rename_project(self, pid):
        p = self.store.get_project(pid)
        if not p:
            return
        name, ok = QInputDialog.getText(self, tr('Renombrar proyecto'), tr('Nuevo nombre:'), text=p['name'])
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
        if QMessageBox.question(self, tr('Confirmar'), tr('¿Eliminar el proyecto "{0}" y todos sus sistemas y riesgos?').format(p["name"])
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
            QMessageBox.information(self, tr('Sin proyecto'), tr('Primero crea o selecciona un proyecto.'))
            return None
        return sel[1]

    def _add_kitchen(self, pid=None):
        pid = pid or self._current_project_id_for_add_kitchen()
        if not pid:
            return
        name, ok = QInputDialog.getText(self, tr('Nuevo sistema'), tr('Nombre del sistema:'))
        if ok and name.strip():
            k = self.store.add_kitchen(pid, name.strip())
            self._refresh_tree(select_kind=ROLE_KITCHEN, select_pid=pid, select_kid=k['id'])

    def _rename_kitchen(self, pid, kid):
        k = self.store.get_kitchen(pid, kid)
        if not k:
            return
        name, ok = QInputDialog.getText(self, tr('Renombrar sistema'), tr('Nuevo nombre:'), text=k['name'])
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
        if QMessageBox.question(self, tr('Confirmar'), tr('¿Eliminar el sistema "{0}" y todos sus riesgos?').format(k["name"])
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
        system = systems.for_project(p)
        self.stack.setCurrentWidget(self.page_project)
        self.footer.setText(system.disclaimer_short)
        self.project_title_label.setText(p['name'])
        self.project_brand_label.setText(tr('Marca: {0}').format(system.label))
        has_eq = self.store.project_has_equipment(p)
        self.btn_change_brand.setEnabled(not has_eq)
        self.btn_change_brand.setToolTip(tr('Solo se puede cambiar mientras el proyecto no tenga riesgos.')
                                         if has_eq else tr('Cambiar la marca de este proyecto.'))
        self.project_quote_edit.setText(p.get('quoteNumber', ''))
        self.kitchens_table.setHorizontalHeaderLabels(
            [tr('Sistema'), tr('Riesgos'), system.flow_label, tr('Cilindros') if system.supports_cylinder_choice else tr('Tanques')])

        has_equipment = any(k.get('equipment') for k in p.get('kitchens', []))
        self.project_pdf_btn.setEnabled(has_equipment)

        self.kitchens_table.setRowCount(0)
        for k in p.get('kitchens', []):
            s = system.kitchen_summary(k)
            row = self.kitchens_table.rowCount()
            self.kitchens_table.insertRow(row)
            name_item = QTableWidgetItem(k['name'])
            name_item.setData(Qt.UserRole, k['id'])
            self.kitchens_table.setItem(row, 0, name_item)
            self.kitchens_table.setItem(row, 1, QTableWidgetItem(str(s['itemCount'])))
            self.kitchens_table.setItem(row, 2, QTableWidgetItem(E.fmt_num(s['totalFlow'])))
            self.kitchens_table.setItem(row, 3, QTableWidgetItem(system.containers_short(s)))

        ps = system.project_summary(p)
        parts = [tr('<b>Sistemas:</b> {0}').format(len(p['kitchens']))]
        parts += [f"<b>{label.strip()}:</b> {value}" for label, value in system.project_rows(ps)]
        self.project_summary_label.setText(tr(' &nbsp;&nbsp; ').join(parts))
        self._fill_nozzle_table(self.project_nozzle_table, ps['nozzleTotals'], system)
        self.project_responsible_edit.setText(self.store.data.get('lastResponsible', ''))

    # ------------------------------------------------------------------
    # Mostrar sistema
    # ------------------------------------------------------------------
    def _show_kitchen(self, pid, kid):
        k = self.store.get_kitchen(pid, kid)
        if not k:
            self.stack.setCurrentWidget(self.page_empty)
            return
        system = systems.for_project(self.store.get_project(pid))
        self.stack.setCurrentWidget(self.page_kitchen)
        self.footer.setText(system.disclaimer_short)
        self.kitchen_title_label.setText(f"{k['name']}  —  {system.label}")
        self.kitchen_pdf_btn.setEnabled(bool(k.get('equipment')))
        self.tank_box.setVisible(system.supports_tank_override)
        self.cylinder_box.setVisible(system.supports_cylinder_choice)
        self.equipment_table.setHorizontalHeaderLabels(
            [tr('Tipo'), tr('Marca / Modelo'), tr('Largo x Ancho'), tr('Profundidad'), tr('Boquillas'),
             tr('Flow pts') if system.supports_cylinder_choice else tr('Flow'), tr('Altura')])

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
            type_item = QTableWidgetItem(system.category_display_label(item))
            type_item.setData(Qt.UserRole, item['id'])
            self.equipment_table.setItem(row, 0, type_item)
            brand_model = ' '.join(x for x in [item.get('brand'), item.get('model')] if x) or '—'
            self.equipment_table.setItem(row, 1, QTableWidgetItem(brand_model))
            self.equipment_table.setItem(row, 2, QTableWidgetItem(system.dimensions_display(item) or '—'))
            self.equipment_table.setItem(row, 3, QTableWidgetItem(system.depth_display(item) or '—'))
            nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (r.get('nozzles') or [])) or '—'
            self.equipment_table.setItem(row, 4, QTableWidgetItem(nozz_txt))
            self.equipment_table.setItem(row, 5, QTableWidgetItem(E.fmt_num(r.get('flowNumber'))))
            self.equipment_table.setItem(row, 6, QTableWidgetItem(r.get('heightRange', '—')))

        s = system.kitchen_summary(k)
        if system.supports_tank_override:
            self._show_ansul_tank_summary(s)
        else:
            self._fill_cylinder_combo(system, s)
            self.kitchen_summary_label.setText('<br>'.join(f'<b>{label}:</b> {value}'
                                                           for label, value in system.summary_rows(s)))
        notes = system.summary_notes(s)
        if notes:
            self.kitchen_note_label.setText('<br><br>'.join(notes))
            self.kitchen_note_label.setVisible(True)
        else:
            self.kitchen_note_label.setVisible(False)
        self._fill_nozzle_table(self.kitchen_nozzle_table, s['nozzleTotals'], system)
        self.kitchen_responsible_edit.setText(self.store.data.get('lastResponsible', ''))

    def _show_ansul_tank_summary(self, s):
        tanks = s['tanks']
        tank_lines = []
        if tanks['tankCount']:
            counts = E.tank_counts(tanks['tanks'])
            for g in sorted(counts.keys(), reverse=True):
                tank_lines.append(tr('Tanque de {0} gal × {1}').format(g, counts[g]))
        tank_txt = '<br>'.join(tank_lines) if tank_lines else tr('Sin riesgos calculados todavía')
        tanks_label = tr('Tanques (selección manual):') if tanks.get('manual') else tr('Tanques:')
        self.kitchen_summary_label.setText(
            tr('<b>Flow number total:</b> {0}<br><b>{1}</b><br>{2}<br><b>Galonaje total de agente:</b> '
               '{3} gal<br><b>Cartucho — opción N2:</b> {4}<br><b>Cartucho — opción CO2 (alternativa, no '
               'ambos):</b> {5}').format(E.fmt_num(s['totalFlow']), tanks_label, tank_txt, E.fmt_num(tanks.get('totalGallons')), tanks.get('n2') or '—', tanks.get('co2') or '—'))

    def _fill_cylinder_combo(self, system, s):
        options = system.cylinder_options(s)
        chosen = (s.get('chosen') or {}).get('cylinders')
        self.cylinder_combo.blockSignals(True)
        self.cylinder_combo.clear()
        for label, cyls in options:
            self.cylinder_combo.addItem(label, cyls)
        if not options:
            self.cylinder_combo.addItem(tr('Sin riesgos calculados todavía'), None)
        idx = next((i for i, (_l, c) in enumerate(options) if c == chosen), 0)
        self.cylinder_combo.setCurrentIndex(idx)
        self.cylinder_combo.setEnabled(bool(options))
        self.cylinder_combo.blockSignals(False)

    def _on_cylinder_choice_changed(self, idx):
        pid, kid = self._current_kitchen_ids()
        if not pid or idx < 0:
            return
        cyls = self.cylinder_combo.itemData(idx)
        if cyls:
            self.store.set_kitchen_cylinder_choice(pid, kid, cyls)
            self._show_kitchen(pid, kid)

    def _fill_nozzle_table(self, table, nozzle_totals, system=None):
        system = system or systems.get(None)
        cols = system.nozzle_columns()
        table.setRowCount(0)
        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        for code in sorted(nozzle_totals.keys()):
            row = table.rowCount()
            table.insertRow(row)
            for c, value in enumerate(system.nozzle_row(code, nozzle_totals[code])):
                table.setItem(row, c, QTableWidgetItem(value))

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
        system = systems.for_project(self.store.get_project(pid))
        dlg = EquipmentDialog(self.store, parent=self, system=system)
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
        system = systems.for_project(self.store.get_project(pid))
        dlg = EquipmentDialog(self.store, existing_item=item, parent=self, system=system)
        if dlg.exec() == EquipmentDialog.Accepted and dlg.result_item:
            self.store.update_equipment(pid, kid, eid, dlg.result_item)
            self._show_kitchen(pid, kid)

    def _delete_equipment(self):
        pid, kid = self._current_kitchen_ids()
        eid = self._selected_equipment_id()
        if not pid or not eid:
            return
        if QMessageBox.question(self, tr('Confirmar'), tr('¿Eliminar este riesgo?')) == QMessageBox.Yes:
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
        default_name = f"KitchenSuppressionCalculator_{report.pdf_sanitize_filename(k['name'])}_{date}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, tr('Guardar reporte PDF de sistema'), default_name, tr('PDF (*.pdf)'))
        if not path:
            return
        try:
            report.build_kitchen_report_pdf(p, k, path, responsible=responsible, date=date,
                                             quote_number=p.get('quoteNumber', ''))
        except Exception as e:
            QMessageBox.critical(self, tr('Error al generar PDF'), str(e))
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
        default_name = f"KitchenSuppressionCalculator_{report.pdf_sanitize_filename(p['name'])}_{date}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, tr('Guardar reporte PDF del proyecto'), default_name, tr('PDF (*.pdf)'))
        if not path:
            return
        try:
            report.build_project_report_pdf(p, path, responsible=responsible, date=date,
                                             quote_number=p.get('quoteNumber', ''))
        except Exception as e:
            QMessageBox.critical(self, tr('Error al generar PDF'), str(e))
            return
        self._offer_open_file(path)

    def _offer_open_file(self, path):
        if QMessageBox.question(self, tr('PDF generado'), tr('El reporte se guardó en:\n{0}\n\n¿Abrirlo ahora?').format(path)
                                 ) == QMessageBox.Yes:
            try:
                if sys.platform.startswith('win'):
                    os.startfile(path)  # noqa
                elif sys.platform == 'darwin':
                    os.system('open "{0}"'.format(path))
                else:
                    os.system('xdg-open "{0}"'.format(path))
            except Exception:
                webbrowser.open(path)

    # ------------------------------------------------------------------
    # Respaldo / restauración
    # ------------------------------------------------------------------
    def _backup_data(self):
        default_name = f'KitchenSuppressionCalculator_respaldo_{today_iso()}.json'
        path, _ = QFileDialog.getSaveFileName(self, tr('Guardar respaldo de datos'), default_name, tr('JSON (*.json)'))
        if not path:
            return
        try:
            self.store.export_backup(path)
            QMessageBox.information(self, tr('Respaldo guardado'), tr('Se guardó el respaldo en:\n{0}').format(path))
        except Exception as e:
            QMessageBox.critical(self, tr('Error al respaldar'), str(e))

    def _restore_data(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('Restaurar respaldo de datos'), '', tr('JSON (*.json)'))
        if not path:
            return
        if QMessageBox.question(self, tr('Confirmar restauración'),
                                 tr('Esto reemplazará todos los proyectos, sistemas y catálogo propio actuales con el '
                                    'contenido del respaldo. ¿Continuar?')) != QMessageBox.Yes:
            return
        try:
            self.store.import_backup(path)
            self._refresh_tree()
            QMessageBox.information(self, tr('Restauración completa'), tr('Los datos se restauraron correctamente.'))
        except Exception as e:
            QMessageBox.critical(self, tr('Error al restaurar'), str(e))

    # ------------------------------------------------------------------
    # Catálogo / referencia / acerca de
    # ------------------------------------------------------------------
    def _open_catalog_manager(self):
        dlg = CatalogManagerDialog(self.store, parent=self)
        dlg.exec()

    def _open_reference(self):
        dlg = ReferenceDialog(parent=self)
        dlg.exec()

    def _open_buckeye_reference(self):
        from .buckeye_reference_dialog import BuckeyeReferenceDialog
        dlg = BuckeyeReferenceDialog(parent=self)
        dlg.exec()

    def _open_settings(self):
        from .settings_dialog import SettingsDialog
        dlg = SettingsDialog(parent=self)
        dlg.exec()

    def _open_unit_converter(self):
        dlg = UnitConverterDialog(parent=self)
        dlg.exec()

    def _show_about(self):
        QMessageBox.information(self, tr('Acerca de Kitchen Suppression Calculator'),
                                 tr('Kitchen Suppression Calculator\n\nCalculadora de apoyo para el diseño preliminar de sistemas de '
                                    'supresión para cocinas comerciales:\n• ANSUL(R) R-102 — manual R-102 (Part No. 418087) y '
                                    'Hoja Resumen F-2015158-01_LAS.\n• Buckeye Kitchen Mister — manual técnico BFR-TM Rev. 6 '
                                    '(2020-02-01).\n\nLa marca se elige al crear cada proyecto.\n\n')
                                 + tr('Autor: {0}\nLicencia: GNU GPL v3.0 — software libre y gratuito. Puede usarse, '
                                      'copiarse y modificarse; las versiones modificadas que se distribuyan deben '
                                      'conservar la misma licencia.').format(AUTHOR) + '\n\n'
                                 + DISCLAIMER_SHORT + '\n\n' + systems.get('buckeye_bfr').disclaimer_short)

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self.store.save()
        event.accept()
