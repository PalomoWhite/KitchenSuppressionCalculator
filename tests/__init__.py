import os

# Las pruebas comparan textos en español: forzar el idioma, sin importar
# lo que el usuario tenga en Configuración.
os.environ['ANSULCALC_LANG'] = 'es'
