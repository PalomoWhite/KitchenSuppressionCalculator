# -*- coding: utf-8 -*-
"""
Configuración: idioma de la interfaz y tema (claro / oscuro).

- El tema se aplica al momento.
- El idioma se aplica al reiniciar (los textos de las tablas se traducen al
  arrancar); el diálogo ofrece reiniciar en ese momento.
"""
import sys

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel,
                                QMessageBox, QApplication)

from .. import settings, i18n
from ..i18n import tr
from . import style
from .style import set_role

# Cada idioma se muestra en su propio idioma, para que siempre se reconozca.
LANGUAGE_CHOICES = [('es', 'Español'), ('en', 'English')]


def restart_app():
    """Abre una nueva instancia del programa y cierra la actual."""
    if getattr(sys, 'frozen', False):          # ejecutable de PyInstaller
        program, args = sys.executable, sys.argv[1:]
    else:
        program, args = sys.executable, sys.argv
    QProcess.startDetached(program, args)
    QApplication.instance().quit()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Configuración'))
        self.setMinimumWidth(420)
        self.saved = settings.load()
        self.language_changed = False

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.language_combo = QComboBox()
        for code, label in LANGUAGE_CHOICES:
            self.language_combo.addItem(label, code)
        self.language_combo.setCurrentIndex([c for c, _ in LANGUAGE_CHOICES].index(self.saved['language']))
        form.addRow(tr('Idioma / Language:'), self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr('Claro'), 'light')
        self.theme_combo.addItem(tr('Oscuro'), 'dark')
        self.theme_combo.setCurrentIndex(0 if self.saved['theme'] == 'light' else 1)
        self.theme_combo.currentIndexChanged.connect(self._preview_theme)
        form.addRow(tr('Tema:'), self.theme_combo)
        layout.addLayout(form)

        note = QLabel(tr('El tema se aplica al momento. El cambio de idioma se aplica al reiniciar el programa; '
                         'los resultados ya calculados se traducen solos al abrirlo.'))
        note.setWordWrap(True)
        set_role(note, 'hint')
        layout.addWidget(note)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self._cancel)
        layout.addWidget(buttons)

    def _preview_theme(self, _idx):
        style.apply_theme(QApplication.instance(), self.theme_combo.currentData())

    def _cancel(self):
        style.apply_theme(QApplication.instance(), self.saved['theme'])
        self.reject()

    def _accept(self):
        language = self.language_combo.currentData()
        theme = self.theme_combo.currentData()
        try:
            settings.save(language=language, theme=theme)
        except OSError as e:
            QMessageBox.critical(self, tr('Configuración'),
                                 tr('No se pudo guardar la configuración:\n{0}').format(e))
            return
        style.apply_theme(QApplication.instance(), theme)
        self.language_changed = language != i18n.language()
        self.accept()
        if self.language_changed:
            # El mensaje va en los dos idiomas: el usuario acaba de cambiarlo.
            answer = QMessageBox.question(
                self.parent(), 'Idioma / Language',
                'El idioma se aplicará al reiniciar el programa. ¿Reiniciar ahora?\n\n'
                'The language will change when the program restarts. Restart now?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if answer == QMessageBox.Yes:
                restart_app()
