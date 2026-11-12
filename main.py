#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ansul Flow Calculator (versión de escritorio en Python / PySide6)
===================================================================

Calculadora de apoyo para el diseño preliminar de sistemas de supresión
ANSUL(R) R-102 para cocinas comerciales.

Basada en:
  - El manual ANSUL(R) R-102 (Part No. 418087).
  - La Hoja Resumen ANSUL F-2015158-01_LAS.
  - La lógica ya validada en la herramienta AnsulCalc.html.

AVISO IMPORTANTE: esta aplicación es una AYUDA DE DISEÑO PRELIMINAR. El
diseño final de cualquier sistema R-102 debe ser verificado y sellado por
un diseñador certificado ANSUL R-102, conforme a NFPA 17A y los códigos
locales aplicables.

Para ejecutar:
    pip install -r requirements.txt
    python main.py
"""
import sys
import os

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtWidgets import QApplication, QMessageBox

from ansul.store import Store
from ansul.ui.main_window import MainWindow
from ansul import settings, i18n
from ansul.ui import style
from ansul.i18n import tr


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Ansul Flow Calculator')
    app.setOrganizationName('AnsulFlowCalculator')
    style.apply_theme(app, settings.load()['theme'])

    # Botones estándar de Qt (Sí/No, Aceptar/Cancelar…) en el idioma elegido.
    qt_translator = QTranslator(app)
    if qt_translator.load(f'qtbase_{i18n.language()}', QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
        app.installTranslator(qt_translator)

    store = Store(path=os.environ.get('ANSULCALC_DB'))
    try:
        store.load()
    except OSError as e:
        QMessageBox.critical(
            None,
            tr('No se pudo abrir la base de datos'),
            tr('No fue posible leer el archivo de proyectos: \n{0}\n\nDetalle: {1}\n\nEl programa se cerrará '
               'para no sobrescribir sus datos. Verifique que el archivo exista y tenga permisos de '
               'lectura. ').format(store.path, e)
        )
        sys.exit(1)

    window = MainWindow(store)
    window.show()

    if store.corrupt_backup:
        QMessageBox.warning(
            window,
            tr('El archivo de proyectos "esta dañado"'),
            tr('El archivo de proyectos estaba dañado y no se pudo leer.\n\nSe guardó una copia intacta en: '
               '\n{0}\n\nEl programa inició con una lista vacía. Conserve esa copia y comuníquese con '
               'soporte técnico para intentar recuperarla').format(store.corrupt_backup)
        )

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
