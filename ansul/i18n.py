# -*- coding: utf-8 -*-
"""
Traducción de la interfaz (español / inglés).

- Todo texto que ve el usuario se escribe en ESPAÑOL en el código y se
  envuelve con tr():           tr('Nuevo proyecto…')
- Si el texto lleva datos, se usa una plantilla con format():
                               tr('Sistema {0}').format(n)
- Las traducciones al inglés viven en i18n_en.py (llave = texto en español).
  Si falta una traducción se muestra el texto en español (nunca truena).

El idioma se decide UNA vez, al arrancar: variable de entorno
ANSULCALC_LANG (las pruebas la usan) o, si no existe, settings.json.
Cambiar el idioma desde Configuración se aplica al reiniciar el programa.
"""
import os

from . import settings

LANG = os.environ.get('ANSULCALC_LANG') or settings.load()['language']
if LANG not in settings.LANGUAGES:
    LANG = 'es'

_CATALOG = None


def _catalog():
    global _CATALOG
    if _CATALOG is None:
        if LANG == 'en':
            from .i18n_en import EN
            _CATALOG = EN
        else:
            _CATALOG = {}
    return _CATALOG


def tr(text):
    """Texto en el idioma activo (español = el mismo texto)."""
    if LANG == 'es' or not text:
        return text
    return _catalog().get(text, text)


def language():
    return LANG
