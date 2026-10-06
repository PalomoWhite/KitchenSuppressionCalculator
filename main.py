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

from PySide6.QtWidgets import QApplication, QMessageBox

from ansul.store import Store
from ansul.ui.main_window import MainWindow
from ansul.ui.style import STYLE_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Ansul Flow Calculator')
    app.setOrganizationName('AnsulFlowCalculator')
    app.setStyleSheet(STYLE_QSS)

    store = Store(path=os.environ.get('ANSULCALC_DB'))
    try:
        store.load()
    except OSError as e:
        QMessageBox.critical(
            None,
            'No se pudo abrir la base de datos',
            f'No fue posible leer el archivo de proyectos: \n{store.path}\n\n'
            f'Detalle: {e}\n\n'
            'El programa se cerrara para no sobrescribir sus datos. '
            'Verifique que el archivo exista y tenga permisos de lectura. '
        )
        sys.exit(1)

    window = MainWindow(store)
    window.show()

    if store.corrupt_backup:
        QMessageBox.warning(
            window,
            'El archivo de proyectos esta dañado',
            'El archivo de proyectos estaba dañado y no se pudo leer.\n\n'
            f'Se guardó una copia intacta en: \n{store.corrupt_backup}\n\n'
            'El programa inició con una lista vacía. Conserve esa copia '
            'y comuníquese con soporte técnico para intentar recuperarla'
        )

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
