# -*- coding: utf-8 -*-
"""
Convertidor rápido de pies <-> metros (menú Herramientas). Utilidad general
solicitada para apoyar la captura de medidas (p.ej. al convertir planos en
pies a las medidas en metros que ahora captura la categoría de Pleno).
"""
from PySide6.QtCore import QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QDialogButtonBox

from .. import engine as E
from ..i18n import tr


class UnitConverterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Convertidor de unidades — pies / metros'))
        self.setMinimumWidth(340)
        self._updating = False

        outer = QVBoxLayout(self)
        outer.addWidget(QLabel(tr('Escriba un valor en cualquiera de los dos campos; el otro se actualiza automáticamente (1 '
                                  'm = 3.28084 ft).')))

        form = QFormLayout()
        validator = QDoubleValidator(-1e9, 1e9, 6)
        validator.setLocale(QLocale(QLocale.C))

        self.ft_edit = QLineEdit()
        self.ft_edit.setValidator(validator)
        self.ft_edit.setPlaceholderText('0')
        form.addRow(tr('Pies (ft):'), self.ft_edit)

        self.m_edit = QLineEdit()
        self.m_edit.setValidator(validator)
        self.m_edit.setPlaceholderText('0')
        form.addRow(tr('Metros (m):'), self.m_edit)

        outer.addLayout(form)

        self.ft_edit.textEdited.connect(self._on_ft_changed)
        self.m_edit.textEdited.connect(self._on_m_changed)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        outer.addWidget(buttons)

    def _on_ft_changed(self, text):
        if self._updating:
            return
        self._updating = True
        try:
            ft = float(text)
            self.m_edit.setText(E.fmt_num(E.ft_to_m(ft)))
        except ValueError:
            self.m_edit.setText('')
        self._updating = False

    def _on_m_changed(self, text):
        if self._updating:
            return
        self._updating = True
        try:
            m = float(text)
            self.ft_edit.setText(E.fmt_num(E.m_to_ft(m)))
        except ValueError:
            self.ft_edit.setText('')
        self._updating = False
