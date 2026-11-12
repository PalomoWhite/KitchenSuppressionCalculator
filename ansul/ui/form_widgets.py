# -*- coding: utf-8 -*-
"""
Utilidades para construir formularios dinámicos a partir de las
especificaciones declarativas de ansul.category_defs (lista de dicts con
'key', 'type', 'label', etc.) — es el equivalente en Qt de las funciones
numInput()/selectInput()/toggleInput() de AnsulCalc.html.
"""
from PySide6.QtCore import Qt, QLocale, Signal, QTimer
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox,
                                QLabel, QVBoxLayout)

from .style import set_role


class DynamicForm(QWidget):
    """Formulario que se reconstruye cada vez que cambian los campos
    (algunas categorías muestran/ocultan campos según el valor de otro,
    p.ej. 'hasDripboard' en freidoras).

    Señales:
      changed           -- cambió el valor de un campo "normal": basta con
                            recalcular el resultado.
      structure_changed -- cambió un campo marcado con 'reflow': True en su
                            especificación (p.ej. el toggle "¿tiene
                            escurridor?"), lo que puede cambiar QUÉ campos
                            deben mostrarse. El que escucha esta señal debe
                            reconstruir el formulario completo (y de paso
                            recalcular).
    """

    changed = Signal()
    structure_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QFormLayout(self)
        self._layout.setLabelAlignment(Qt.AlignLeft)
        self._widgets = {}  # key -> widget
        self._reflow_keys = set()

    def clear(self):
        while self._layout.rowCount():
            self._layout.removeRow(0)
        self._widgets = {}

    def build(self, field_specs, values):
        """field_specs: lista de dicts (ver category_defs). values: dict
        mutable de valores actuales — se lee para precargar y se sigue
        usando como fuente de verdad tras cada edición."""
        self.clear()
        self._reflow_keys = {spec['key'] for spec in field_specs if spec.get('reflow')}
        for spec in field_specs:
            key = spec['key']
            label_text = spec.get('label', key)
            ftype = spec['type']

            if ftype == 'info':
                lbl = QLabel(label_text)
                lbl.setWordWrap(True)
                set_role(lbl, 'info')
                self._layout.addRow(lbl)
                continue

            hint = spec.get('hint')
            label_widget = QLabel(label_text + (' *' if spec.get('required', True) and ftype != 'toggle' else ''))

            if ftype == 'number':
                w = QLineEdit()
                validator = QDoubleValidator(-1e9, 1e9, 6)
                # Forzamos el separador decimal "." (punto) sin importar la
                # configuración regional de Windows del usuario, porque el
                # motor de cálculo interpreta los números con float() de
                # Python (que solo acepta punto decimal).
                validator.setLocale(QLocale(QLocale.C))
                w.setValidator(validator)
                current = values.get(key, spec.get('default', ''))
                w.setText('' if current is None else str(current))
                if hint:
                    w.setPlaceholderText(hint)
                    w.setToolTip(hint)
                w.textChanged.connect(lambda text, k=key: self._on_value_changed(k, text))
                self._widgets[key] = w
                self._layout.addRow(label_widget, w)

            elif ftype == 'select':
                w = QComboBox()
                options = spec.get('options', [])
                default = values.get(key, spec.get('default'))
                sel_index = 0
                for i, opt in enumerate(options):
                    w.addItem(opt['label'], opt['value'])
                    if str(opt['value']) == str(default):
                        sel_index = i
                w.setCurrentIndex(sel_index)
                if default is not None and key not in values:
                    values[key] = default
                w.currentIndexChanged.connect(lambda idx, k=key, cb=w: self._on_value_changed(k, cb.itemData(idx)))
                if hint:
                    w.setToolTip(hint)
                self._widgets[key] = w
                self._layout.addRow(label_widget, w)

            elif ftype == 'toggle':
                w = QCheckBox(label_text)
                default = values.get(key, spec.get('default', False))
                w.setChecked(bool(default))
                if key not in values:
                    values[key] = bool(default)
                if hint:
                    w.setToolTip(hint)
                w.toggled.connect(lambda checked, k=key: self._on_value_changed(k, checked))
                self._widgets[key] = w
                self._layout.addRow(w)

            if hint and ftype in ('number',):
                hint_lbl = QLabel(hint)
                hint_lbl.setWordWrap(True)
                set_role(hint_lbl, 'hint')
                self._layout.addRow('', hint_lbl)

        self._values = values

    def _on_value_changed(self, key, value):
        self._values[key] = value
        if key in self._reflow_keys:
            # No reconstruir el formulario aquí mismo: el widget que cambió
            # (p. ej. la casilla "¿Tiene escurridor?") sigue procesando el
            # clic, y reconstruir lo destruiría → cierre de la app en macOS.
            # singleShot(0) espera a que termine el clic.
            QTimer.singleShot(0, self.structure_changed.emit)
        else:
            self.changed.emit()
