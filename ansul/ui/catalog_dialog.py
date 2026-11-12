# -*- coding: utf-8 -*-
"""
Diálogos de catálogo de modelos:
  - CatalogPickerDialog: para elegir una ficha (del manual o agregada por el
    usuario) al capturar un equipo — equivalente a openCatalogModal().
  - CatalogManagerDialog: para administrar (agregar/editar/eliminar) el
    catálogo propio del usuario — equivalente a openCatalogEntryModal() y
    renderCatalogManageView().
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
                                QComboBox, QPushButton, QDialogButtonBox, QListWidget, QListWidgetItem,
                                QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
                                QSpinBox, QTextEdit, QWidget)

from .. import data as D
from .. import engine as E
from ..i18n import tr


def _entry_summary(entry):
    nozz = entry.get('nozzles')
    if nozz:
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in nozz)
    else:
        nozz_txt = tr('Sin boquilla fija (ver notas)')
    fuel = f" · {D.FUEL_LABELS.get(entry['fuel'], entry['fuel'])}" if entry.get('fuel') else ''
    tag = tr(' [tu catálogo]') if entry.get('source') == 'user' else ''
    return f"{entry.get('brand','')} — {entry.get('model','')}{tag}\n{nozz_txt}{fuel}"


class CatalogPickerDialog(QDialog):
    def __init__(self, category, custom_catalog, parent=None):
        super().__init__(parent)
        self.category = category
        self.selected_entry = None
        self.setWindowTitle(tr('Catálogo de modelos — {0}').format(D.CATEGORY_LABELS.get(category, category)))
        self.setMinimumSize(560, 420)

        layout = QVBoxLayout(self)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr('Buscar por marca o modelo…'))
        self.search_edit.textChanged.connect(self._refresh_list)
        layout.addWidget(self.search_edit)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(lambda _: self._accept_selection())
        layout.addWidget(self.list_widget)

        self.entries = E.catalog_entries_for_category(category, custom_catalog)
        self._refresh_list()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if not self.entries:
            info = QLabel(tr('No hay fichas de catálogo para esta categoría todavía. Puede continuar capturando las '
                             'medidas manualmente, o agregar una ficha propia desde el menú Catálogo > Administrar mi '
                             'catálogo.'))
            info.setWordWrap(True)
            layout.addWidget(info)

    def _refresh_list(self):
        query = self.search_edit.text().strip().lower()
        self.list_widget.clear()
        for entry in self.entries:
            haystack = f"{entry.get('brand','')} {entry.get('model','')}".lower()
            if query and query not in haystack:
                continue
            item = QListWidgetItem(_entry_summary(entry))
            item.setData(Qt.UserRole, entry)
            self.list_widget.addItem(item)

    def _accept_selection(self):
        item = self.list_widget.currentItem()
        if not item:
            self.reject()
            return
        self.selected_entry = item.data(Qt.UserRole)
        self.accept()


class NozzleRowsEditor(QWidget):
    """Editor de la lista de boquillas [{code,qty}] de una ficha de catálogo."""

    def __init__(self, nozzles=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([tr('Boquilla'), tr('Cantidad')])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(tr('+ Agregar boquilla'))
        add_btn.clicked.connect(lambda: self._add_row())
        rm_btn = QPushButton(tr('Quitar seleccionada'))
        rm_btn.clicked.connect(self._remove_selected)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rm_btn)
        layout.addLayout(btn_row)

        for n in (nozzles or []):
            self._add_row(n.get('code'), n.get('qty', 1))
        if not nozzles:
            pass  # sin boquilla fija (ficha informativa) — se deja vacío

    def _add_row(self, code=None, qty=1):
        row = self.table.rowCount()
        self.table.insertRow(row)
        combo = QComboBox()
        for c in D.NOZZLES.keys():
            combo.addItem(c)
        if code:
            idx = combo.findText(code)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        self.table.setCellWidget(row, 0, combo)
        spin = QSpinBox()
        spin.setRange(1, 50)
        spin.setValue(int(qty or 1))
        self.table.setCellWidget(row, 1, spin)

    def _remove_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def get_nozzles(self):
        out = []
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 0)
            spin = self.table.cellWidget(row, 1)
            if combo and spin:
                out.append({'code': combo.currentText(), 'qty': spin.value()})
        return out or None


class CatalogEntryEditDialog(QDialog):
    """Alta/edición de una ficha del catálogo propio del usuario."""

    def __init__(self, entry=None, parent=None):
        super().__init__(parent)
        self.entry = dict(entry) if entry else {}
        self.setWindowTitle(tr('Editar ficha de catálogo') if entry else tr('Nueva ficha de catálogo'))
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.category_combo = QComboBox()
        for key in D.CATEGORY_ORDER:
            self.category_combo.addItem(D.CATEGORY_LABELS[key], key)
        if self.entry.get('category'):
            idx = D.CATEGORY_ORDER.index(self.entry['category']) if self.entry['category'] in D.CATEGORY_ORDER else 0
            self.category_combo.setCurrentIndex(idx)
        form.addRow(tr('Categoría'), self.category_combo)

        self.brand_edit = QLineEdit(self.entry.get('brand', ''))
        self.model_edit = QLineEdit(self.entry.get('model', ''))
        form.addRow(tr('Marca'), self.brand_edit)
        form.addRow(tr('Modelo'), self.model_edit)

        self.fuel_combo = QComboBox()
        self.fuel_combo.addItem(tr('(sin especificar)'), None)
        for k, v in D.FUEL_LABELS.items():
            self.fuel_combo.addItem(v, k)
        if self.entry.get('fuel'):
            idx = self.fuel_combo.findData(self.entry['fuel'])
            if idx >= 0:
                self.fuel_combo.setCurrentIndex(idx)
        form.addRow(tr('Combustible'), self.fuel_combo)

        self.hmin_edit = QLineEdit('' if self.entry.get('hmin') is None else str(self.entry['hmin']))
        self.hmax_edit = QLineEdit('' if self.entry.get('hmax') is None else str(self.entry['hmax']))
        h_row = QHBoxLayout()
        h_row.addWidget(self.hmin_edit)
        h_row.addWidget(QLabel('a'))
        h_row.addWidget(self.hmax_edit)
        form.addRow(tr('Altura de boquilla (in), min/max'), h_row)

        self.surfw_edit = QLineEdit('' if self.entry.get('surfaceW') is None else str(self.entry['surfaceW']))
        self.surfd_edit = QLineEdit('' if self.entry.get('surfaceD') is None else str(self.entry['surfaceD']))
        s_row = QHBoxLayout()
        s_row.addWidget(self.surfw_edit)
        s_row.addWidget(QLabel('x'))
        s_row.addWidget(self.surfd_edit)
        form.addRow(tr('Superficie (ancho x fondo, in) — opcional'), s_row)

        layout.addLayout(form)

        layout.addWidget(QLabel(tr('Boquillas (deje vacío si el manual no especifica una cantidad fija):')))
        self.nozzle_editor = NozzleRowsEditor(self.entry.get('nozzles'))
        layout.addWidget(self.nozzle_editor)

        layout.addWidget(QLabel(tr('Notas / ubicación de montaje:')))
        self.notes_edit = QTextEdit(self.entry.get('notes', ''))
        self.notes_edit.setMaximumHeight(80)
        layout.addWidget(self.notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _parse_float(self, text):
        text = text.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _on_accept(self):
        brand = self.brand_edit.text().strip()
        model = self.model_edit.text().strip()
        if not brand or not model:
            QMessageBox.warning(self, tr('Datos incompletos'), tr('Indique al menos marca y modelo.'))
            return
        self.entry.update({
            'category': self.category_combo.currentData(),
            'brand': brand,
            'model': model,
            'fuel': self.fuel_combo.currentData(),
            'hmin': self._parse_float(self.hmin_edit.text()),
            'hmax': self._parse_float(self.hmax_edit.text()),
            'surfaceW': self._parse_float(self.surfw_edit.text()),
            'surfaceD': self._parse_float(self.surfd_edit.text()),
            'nozzles': self.nozzle_editor.get_nozzles(),
            'notes': self.notes_edit.toPlainText().strip(),
        })
        self.accept()


class CatalogManagerDialog(QDialog):
    """Administra el catálogo propio del usuario (customCatalog)."""

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle(tr('Mi catálogo de equipos'))
        self.setMinimumSize(560, 420)

        layout = QVBoxLayout(self)
        info = QLabel(tr('Fichas de equipos que has agregado (además de las 65 que ya vienen del manual R-102). Se '
                         'guardan junto con tus proyectos y se incluyen en el respaldo/restauración.'))
        info.setWordWrap(True)
        layout.addWidget(info)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(tr('Agregar ficha…'))
        add_btn.clicked.connect(self._add_entry)
        edit_btn = QPushButton(tr('Editar…'))
        edit_btn.clicked.connect(self._edit_entry)
        del_btn = QPushButton(tr('Eliminar'))
        del_btn.clicked.connect(self._delete_entry)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.accept)
        close_buttons.accepted.connect(self.accept)
        layout.addWidget(close_buttons)

        self._refresh()

    def _refresh(self):
        self.list_widget.clear()
        for entry in self.store.data.get('customCatalog', []):
            label = D.CATEGORY_LABELS.get(entry.get('category'), entry.get('category'))
            item = QListWidgetItem(f"[{label}] {_entry_summary(entry)}")
            item.setData(Qt.UserRole, entry['id'])
            self.list_widget.addItem(item)

    def _add_entry(self):
        dlg = CatalogEntryEditDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.store.add_catalog_entry(dlg.entry)
            self._refresh()

    def _edit_entry(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        entry_id = item.data(Qt.UserRole)
        entry = self.store.get_catalog_entry(entry_id)
        if not entry:
            return
        dlg = CatalogEntryEditDialog(entry=entry, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.store.update_catalog_entry(entry_id, dlg.entry)
            self._refresh()

    def _delete_entry(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        entry_id = item.data(Qt.UserRole)
        if QMessageBox.question(self, tr('Confirmar'), tr('¿Eliminar esta ficha de tu catálogo?')) == QMessageBox.Yes:
            self.store.delete_catalog_entry(entry_id)
            self._refresh()
