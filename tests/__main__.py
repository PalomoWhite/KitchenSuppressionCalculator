# -*- coding: utf-8 -*-
"""Corre TODAS las pruebas:  python -m tests"""
from tests import test_engine, test_buckeye, test_i18n

if __name__ == '__main__':
    print('=== Motor ANSUL R-102 ===')
    test_engine.run_all()
    print('\n=== Buckeye Kitchen Mister + registro de marcas ===')
    test_buckeye.run_all()
    print('\n=== Idioma y configuración ===')
    test_i18n.run_all()
    print('\nTodas las pruebas pasaron.')
