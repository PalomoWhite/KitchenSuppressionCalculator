# -*- coding: utf-8 -*-
"""
Preferencias del usuario (idioma y tema) en un archivo aparte,
settings.json, junto a la base de datos de proyectos.

Va en un archivo propio (no dentro de ansulcalc_db.json) porque el idioma
se tiene que conocer ANTES de cargar el resto del programa: los textos de
las tablas (data.py) se traducen al importarse.

Este módulo no importa nada del resto del programa a propósito.
"""
import json
import os
from pathlib import Path

APP_DIR_NAME = 'KitchenSuppressionCalculator'
# Nombre anterior del programa: si ya existe esa carpeta (proyectos guardados
# antes del cambio de nombre) se sigue usando, para no "perder" nada.
OLD_APP_DIR_NAME = 'AnsulFlowCalculator'
LANGUAGES = ('es', 'en')
THEMES = ('light', 'dark')
DEFAULTS = {'language': 'es', 'theme': 'light'}


def default_data_dir(home=None):
    """Carpeta de datos por defecto: Documentos/KitchenSuppressionCalculator
    (o el home del usuario si no existe una carpeta de Documentos estándar).
    Si existe la carpeta del nombre anterior (AnsulFlowCalculator) y aún no
    la nueva, se usa la anterior."""
    home = Path(home) if home else Path.home()
    base = home
    for c in (home / 'Documents', home / 'Documentos'):
        if c.is_dir():
            base = c
            break
    new, old = base / APP_DIR_NAME, base / OLD_APP_DIR_NAME
    if not new.exists() and old.is_dir():
        return old
    return new


def settings_path():
    db = os.environ.get('ANSULCALC_DB')
    base = Path(db).parent if db else default_data_dir()
    return base / 'settings.json'


def load():
    """Preferencias guardadas; si no hay archivo o está dañado, las de
    fábrica (español, tema claro). Nunca lanza error."""
    data = dict(DEFAULTS)
    try:
        with open(settings_path(), 'r', encoding='utf-8') as f:
            saved = json.load(f)
        if saved.get('language') in LANGUAGES:
            data['language'] = saved['language']
        if saved.get('theme') in THEMES:
            data['theme'] = saved['theme']
    except (OSError, ValueError, AttributeError):
        pass
    return data


def save(**changes):
    data = load()
    for k, v in changes.items():
        if k == 'language' and v not in LANGUAGES:
            raise ValueError(f'Idioma no soportado: {v}')
        if k == 'theme' and v not in THEMES:
            raise ValueError(f'Tema no soportado: {v}')
        data[k] = v
    p = settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)
    return data
