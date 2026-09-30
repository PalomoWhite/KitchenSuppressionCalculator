# -*- coding: utf-8 -*-
"""
Paleta de colores compartida por toda la app Android — los mismos valores
que ansul/ui/style.py usa para la versión de escritorio (azul ANSUL
#0554a3), para que ambas versiones se vean como "la misma app".
"""

PRIMARY = '#0554a3'
PRIMARY_DARK = '#053e78'
PRIMARY_LIGHT = '#eef5ff'
ACCENT = '#2e7d32'
ERROR = '#b71c1c'
ERROR_BG = '#fdf1f1'
OK_BG = '#f1f8f2'
TEXT = '#1e1e1e'
MUTED = '#5a6272'
BORDER = '#cccccc'
CARD_BG = '#ffffff'
SCREEN_BG = '#f4f6fb'


def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return [r, g, b, alpha]
