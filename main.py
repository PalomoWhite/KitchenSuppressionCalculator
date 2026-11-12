#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kitchen Suppression Calculator (versión de escritorio en Python / PySide6)
==========================================================================

Copyright (C) 2026 Miguel Alejandro Gutiérrez Torres

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version. This program is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License (file LICENSE) for more details.

Calculadora de apoyo para el diseño preliminar de sistemas de supresión
para cocinas comerciales: ANSUL(R) R-102 y Buckeye Kitchen Mister.

Basada en:
  - El manual ANSUL(R) R-102 (Part No. 418087).
  - La Hoja Resumen ANSUL F-2015158-01_LAS.
  - El manual técnico Buckeye Kitchen Mister (BFR-TM Rev. 6).
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
    app.setApplicationName('Kitchen Suppression Calculator')
    app.setOrganizationName('KitchenSuppressionCalculator')
    app.setWindowIcon(style.app_icon())
    if sys.platform == 'win32':
        # Para que la barra de tareas de Windows muestre el logotipo del
        # programa y no el de Python al correrlo con "python main.py".
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('KitchenSuppressionCalculator')
        except (AttributeError, OSError):
            pass
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
