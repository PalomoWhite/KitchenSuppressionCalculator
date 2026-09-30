# -*- coding: utf-8 -*-
"""
Diálogo de captura/edición de un equipo/riesgo de cocina — equivalente a
la vista de "formulario de equipo" de AnsulCalc.html (renderEquipmentForm +
buildResultFromState). Construye el formulario dinámicamente según la
categoría elegida y muestra en vivo el resultado (boquillas / flow number)
a medida que el usuario captura datos.
"""
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
                                QComboBox, QPushButton, QDialogButtonBox, QListWidget, QListWidgetItem,
                                QGroupBox, QMessageBox, QWidget, QScrollArea)

from .. import data as D
from .. import engine as E
from .. import category_defs as CD
from .form_widgets import DynamicForm
from .catalog_dialog import CatalogPickerDialog
from .diagram_widget import EquipmentDiagramWidget


class EquipmentDialog(QDialog):
    def __init__(self, store, existing_item=None, parent=None):
        super().__init__(parent)
        self.store = store
        self.existing_item = existing_item
        self.result_item = None

        self.category = (existing_item or {}).get('category', 'fryer')
        self.values = dict((existing_item or {}).get('input') or {})
        self.chosen_idx = (existing_item or {}).get('chosenIdx') or 0
        self.catalog_ref = (existing_item or {}).get('catalogRef')
        self.catalog_result = None
        if self.catalog_ref and self.catalog_ref.get('hasFixedNozzles'):
            self.catalog_result = (existing_item or {}).get('result')

        self.current_calc = None
        self.final_result = None

        self.setWindowTitle('Editar riesgo' if existing_item else 'Agregar riesgo')
        self.setMinimumWidth(520)
        self._build_ui()
        self._on_category_changed(initial=True)

    # ------------------------------------------------------------------
    def _build_ui(self):
        outer = QVBoxLayout(self)

        top_form = QFormLayout()
        self.category_combo = QComboBox()
        for key in D.CATEGORY_ORDER:
            self.category_combo.addItem(D.CATEGORY_LABELS[key], key)
        self.category_combo.setCurrentIndex(D.CATEGORY_ORDER.index(self.category))
        self.category_combo.currentIndexChanged.connect(self._category_index_changed)
        top_form.addRow('Categoría de riesgo', self.category_combo)

        brand_row = QHBoxLayout()
        self.brand_edit = QLineEdit((self.existing_item or {}).get('brand', ''))
        self.model_edit = QLineEdit((self.existing_item or {}).get('model', ''))
        self.brand_edit.setPlaceholderText('Marca (opcional)')
        self.model_edit.setPlaceholderText('Modelo (opcional)')
        brand_row.addWidget(self.brand_edit)
        brand_row.addWidget(self.model_edit)
        top_form.addRow('Marca / Modelo', brand_row)

        catalog_row = QHBoxLayout()
        self.catalog_btn = QPushButton('Buscar en catálogo de modelos…')
        self.catalog_btn.clicked.connect(self._open_catalog_picker)
        self.clear_catalog_btn = QPushButton('Usar mis propias medidas')
        self.clear_catalog_btn.clicked.connect(self._clear_catalog_ref)
        self.clear_catalog_btn.setVisible(bool(self.catalog_ref))
        catalog_row.addWidget(self.catalog_btn)
        catalog_row.addWidget(self.clear_catalog_btn)
        top_form.addRow('', catalog_row)

        self.notes_edit = QLineEdit((self.existing_item or {}).get('notes', ''))
        self.notes_edit.setPlaceholderText('Notas (opcional)')
        top_form.addRow('Notas', self.notes_edit)

        outer.addLayout(top_form)

        self.catalog_banner = QLabel('')
        self.catalog_banner.setWordWrap(True)
        self.catalog_banner.setStyleSheet('background:#eef5ff; color:#0554a3; padding:6px; border-radius:4px;')
        self.catalog_banner.setVisible(False)
        outer.addWidget(self.catalog_banner)

        # Convertidor rápido (m <-> ft, in <-> cm) para apoyar la captura de
        # medidas cuando el plano o la ficha técnica viene en otra unidad —
        # no captura nada del equipo, solo ayuda a convertir antes de teclear
        # el valor en el campo correspondiente de abajo.
        self.converter_group = QGroupBox('Convertidor rápido de unidades')
        converter_layout = QHBoxLayout(self.converter_group)
        self.converter_m_ft = self._build_converter_row('Metros (m):', 'Pies (ft):', E.m_to_ft, E.ft_to_m)
        self.converter_in_cm = self._build_converter_row('Pulgadas (in):', 'Centímetros (cm):', E.in_to_cm, E.cm_to_in)
        converter_layout.addWidget(self.converter_m_ft)
        converter_layout.addWidget(self.converter_in_cm)
        converter_layout.addStretch()
        outer.addWidget(self.converter_group)

        # Formulario dinámico dentro de un scroll (algunas categorías, como
        # el catálogo de modelos por marca, pueden tener textos largos).
        self.form = DynamicForm()
        self.form.changed.connect(self._recompute)
        self.form.structure_changed.connect(self._on_form_structure_changed)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.form)
        scroll.setMinimumHeight(220)

        form_diagram_row = QHBoxLayout()
        form_diagram_row.addWidget(scroll, 3)

        diagram_group = QGroupBox('Diagrama del área protegida')
        diagram_layout = QVBoxLayout(diagram_group)
        self.diagram = EquipmentDiagramWidget()
        diagram_layout.addWidget(self.diagram)
        form_diagram_row.addWidget(diagram_group, 2)

        outer.addLayout(form_diagram_row)

        # Panel de opciones (para categorías con varias boquillas candidatas)
        self.choice_group = QGroupBox('Opciones de boquilla disponibles — elige una')
        choice_layout = QVBoxLayout(self.choice_group)
        self.choice_list = QListWidget()
        self.choice_list.currentRowChanged.connect(self._choice_selected)
        choice_layout.addWidget(self.choice_list)
        self.choice_group.setVisible(False)
        outer.addWidget(self.choice_group)

        # Resultado final
        self.result_label = QLabel('Complete los datos para calcular la boquilla requerida.')
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet('padding:8px; border:1px solid #ccc; border-radius:4px;')
        outer.addWidget(self.result_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        outer.addWidget(self.button_box)

    def _build_converter_row(self, label_a, label_b, a_to_b, b_to_a):
        """Un par de campos enlazados bidireccionalmente: escribir en uno
        actualiza el otro usando las funciones de conversión dadas (p.ej.
        E.m_to_ft / E.ft_to_m). Es el mismo patrón de UnitConverterDialog,
        pero compacto para vivir dentro de este formulario."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        validator = QDoubleValidator(-1e9, 1e9, 6)
        validator.setLocale(QLocale(QLocale.C))

        edit_a = QLineEdit()
        edit_a.setValidator(validator)
        edit_a.setPlaceholderText('0')
        edit_a.setMaximumWidth(70)
        edit_b = QLineEdit()
        edit_b.setValidator(validator)
        edit_b.setPlaceholderText('0')
        edit_b.setMaximumWidth(70)

        row_layout.addWidget(QLabel(label_a))
        row_layout.addWidget(edit_a)
        row_layout.addWidget(QLabel('='))
        row_layout.addWidget(edit_b)
        row_layout.addWidget(QLabel(label_b))

        state = {'updating': False}

        def on_a_changed(text):
            if state['updating']:
                return
            state['updating'] = True
            try:
                edit_b.setText(E.fmt_num(a_to_b(float(text))))
            except ValueError:
                edit_b.setText('')
            state['updating'] = False

        def on_b_changed(text):
            if state['updating']:
                return
            state['updating'] = True
            try:
                edit_a.setText(E.fmt_num(b_to_a(float(text))))
            except ValueError:
                edit_a.setText('')
            state['updating'] = False

        edit_a.textEdited.connect(on_a_changed)
        edit_b.textEdited.connect(on_b_changed)
        # Expuestos por si algún día se quieren leer/limpiar desde pruebas.
        row.edit_a = edit_a
        row.edit_b = edit_b
        return row

    # ------------------------------------------------------------------
    def _category_index_changed(self, idx):
        new_cat = self.category_combo.itemData(idx)
        if new_cat == self.category:
            return
        self.category = new_cat
        self.values = {}
        self.chosen_idx = 0
        self.catalog_ref = None
        self.catalog_result = None
        self.clear_catalog_btn.setVisible(False)
        self.catalog_banner.setVisible(False)
        self._on_category_changed()

    def _on_category_changed(self, initial=False):
        self._rebuild_form()
        self._recompute()

    def _rebuild_form(self):
        cdef = CD.CATEGORY_DEFS[self.category]
        specs = cdef['fields'](self.values)
        self.form.build(specs, self.values)

    def _on_form_structure_changed(self):
        # Un campo "controlador" cambió (p.ej. ¿tiene escurridor?, tipo de
        # protección del asador de cadena, ducto redondo/rectangular): hay
        # que reconstruir el formulario para mostrar/ocultar los campos
        # correspondientes, y luego recalcular con los valores vigentes.
        self._rebuild_form()
        self._recompute()

    # ------------------------------------------------------------------
    def _open_catalog_picker(self):
        dlg = CatalogPickerDialog(self.category, self.store.data.get('customCatalog', []), self)
        if dlg.exec() == QDialog.Accepted and dlg.selected_entry:
            entry = dlg.selected_entry
            self.brand_edit.setText(entry.get('brand', ''))
            self.model_edit.setText(entry.get('model', ''))
            result = E.catalog_entry_to_result(entry)
            self.catalog_ref = {
                'brand': entry.get('brand'), 'model': entry.get('model'), 'notes': entry.get('notes', ''),
                'hmin': entry.get('hmin'), 'hmax': entry.get('hmax'),
                'surfaceW': entry.get('surfaceW'), 'surfaceD': entry.get('surfaceD'), 'fuel': entry.get('fuel'),
                'hasFixedNozzles': bool(result), 'source': entry.get('source', 'manual'),
            }
            self.catalog_result = result
            self.clear_catalog_btn.setVisible(True)
            if result:
                self.catalog_banner.setText(
                    f"Usando datos de catálogo: {entry.get('brand','')} {entry.get('model','')}. "
                    'Las boquillas se tomaron directamente del catálogo (no se calculan por medidas).')
            else:
                self.catalog_banner.setText(
                    f"Referencia de catálogo: {entry.get('brand','')} {entry.get('model','')} — "
                    'el manual no da una cantidad de boquilla fija para este modelo; continúe capturando '
                    'las medidas manualmente abajo.')
            self.catalog_banner.setVisible(True)
            self._recompute()

    def _clear_catalog_ref(self):
        self.catalog_ref = None
        self.catalog_result = None
        self.clear_catalog_btn.setVisible(False)
        self.catalog_banner.setVisible(False)
        self._recompute()

    # ------------------------------------------------------------------
    def _recompute(self):
        cdef = CD.CATEGORY_DEFS[self.category]
        self.diagram.update_diagram(self.category, self.values, self.catalog_ref)

        if self.catalog_result is not None:
            self.choice_group.setVisible(False)
            self.final_result = self.catalog_result
            self._show_result(self.final_result)
            return

        if not CD.has_required_inputs(self.category, self.values):
            self.choice_group.setVisible(False)
            self.final_result = None
            self.result_label.setText('Complete los datos requeridos (*) para calcular la boquilla.')
            self.result_label.setStyleSheet('padding:8px; border:1px solid #ccc; border-radius:4px; color:#666;')
            return

        calc = cdef['compute'](self.values)
        self.current_calc = calc

        if cdef.get('has_choice'):
            matches = calc.get('matches') or []
            if not calc.get('ok') or not matches:
                self.choice_group.setVisible(False)
                self.final_result = None
                msg = cdef['not_fit_msg'](self.values, calc)
                self._show_error(msg)
                return
            self.choice_group.setVisible(True)
            self.choice_list.blockSignals(True)
            self.choice_list.clear()
            for m in matches:
                label = cdef['choice_label'](m)
                sub = cdef['choice_sub'](m)
                item = QListWidgetItem(f'{label}\n{sub}')
                self.choice_list.addItem(item)
            idx = self.chosen_idx if 0 <= self.chosen_idx < len(matches) else 0
            self.choice_list.setCurrentRow(idx)
            self.choice_list.blockSignals(False)
            self.chosen_idx = idx
            self.final_result = cdef['result_from_choice'](calc, idx)
            self._show_result(self.final_result)
        else:
            self.choice_group.setVisible(False)
            if not calc.get('ok'):
                self.final_result = None
                msg = cdef['not_fit_msg'](self.values, calc)
                self._show_error(msg)
                return
            self.final_result = calc.get('result')
            self._show_result(self.final_result)

    def _choice_selected(self, row):
        if row < 0 or not self.current_calc:
            return
        self.chosen_idx = row
        cdef = CD.CATEGORY_DEFS[self.category]
        self.final_result = cdef['result_from_choice'](self.current_calc, row)
        self._show_result(self.final_result)

    def _show_result(self, result):
        if not result:
            self._show_error('No se pudo calcular un resultado.')
            return
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (result.get('nozzles') or [])) or 'Sin boquillas (informativo)'
        text = (f"<b>Boquillas:</b> {nozz_txt} &nbsp;&nbsp; <b>Flow number:</b> {E.fmt_num(result.get('flowNumber'))}<br>"
                f"<b>Altura de montaje:</b> {result.get('heightRange', '—')}<br>"
                f"<b>Detalle:</b> {result.get('detail', '')}")
        self.result_label.setText(text)
        self.result_label.setStyleSheet('padding:8px; border:1px solid #2e7d32; background:#f1f8f2; border-radius:4px;')

    def _show_error(self, msg):
        self.result_label.setText(msg or 'Estas medidas no encajan en ninguna opción estándar del manual R-102.')
        self.result_label.setStyleSheet('padding:8px; border:1px solid #b71c1c; background:#fdf1f1; border-radius:4px; color:#7a1414;')

    # ------------------------------------------------------------------
    def _on_accept(self):
        if not self.final_result:
            QMessageBox.warning(self, 'Datos incompletos',
                                 'Complete los datos necesarios para obtener un resultado válido antes de guardar.')
            return
        self.result_item = {
            'category': self.category,
            'brand': self.brand_edit.text().strip(),
            'model': self.model_edit.text().strip(),
            'notes': self.notes_edit.text().strip(),
            'input': dict(self.values),
            'chosenIdx': self.chosen_idx,
            'catalogRef': self.catalog_ref,
            'result': self.final_result,
        }
        self.accept()
