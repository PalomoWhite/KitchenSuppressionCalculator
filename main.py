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

from PySide6.QtWidgets import QApplication

from ansul.store import Store
from ansul.ui.main_window import MainWindow
from ansul.ui.style import STYLE_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Ansul Flow Calculator')
    app.setOrganizationName('AnsulFlowCalculator')
    app.setStyleSheet(STYLE_QSS)

    store = Store()
    store.load()

    window = MainWindow(store)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
