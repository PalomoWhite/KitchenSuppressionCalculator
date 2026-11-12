import os
import sys

# Las pruebas imprimen acentos y símbolos (≈, ×, →). La consola de Windows
# usa por defecto una codificación antigua (cp1252) que no los soporta y la
# prueba se caía al imprimir; se fuerza UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

# Las pruebas comparan textos en español: forzar el idioma, sin importar
# lo que el usuario tenga en Configuración.
os.environ['ANSULCALC_LANG'] = 'es'
