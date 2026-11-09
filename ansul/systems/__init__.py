# -*- coding: utf-8 -*-
"""
Registro de marcas (registry). La interfaz y el reporte nunca importan una
marca directamente: piden la de cada proyecto con for_project(p).
Ver docs/DISEÑO.md.
"""
from .ansul_r102 import SYSTEM as ANSUL_R102
from .buckeye_bfr.system import SYSTEM as BUCKEYE_BFR

DEFAULT_SYSTEM = ANSUL_R102.key

REGISTRY = {s.key: s for s in (ANSUL_R102, BUCKEYE_BFR)}

# [(key, etiqueta)] en el orden en que se ofrecen al crear un proyecto
CHOICES = [(s.key, s.label) for s in REGISTRY.values()]


def get(key):
    """Marca por clave; si la clave no existe (o es None), ANSUL R-102."""
    return REGISTRY.get(key or DEFAULT_SYSTEM, REGISTRY[DEFAULT_SYSTEM])


def is_valid(key):
    return key in REGISTRY


def for_project(project):
    return get((project or {}).get('system'))
