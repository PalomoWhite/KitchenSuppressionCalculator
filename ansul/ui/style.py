# -*- coding: utf-8 -*-
"""
Tema visual (QSS) de la aplicación — puerto de la paleta y estilo de tarjetas
de AnsulCalc.html (variables :root, .card, .btn/.btn-primary/.btn-secondary/
.btn-danger, .topbar, .section-title, .field label) a Qt Style Sheets, para
que la versión de escritorio se vea como la herramienta web original.
"""
from pathlib import Path

# Logotipo del programa (ventana, barra de tareas, "Acerca de").
ASSETS_DIR = Path(__file__).resolve().parent / 'assets'


def app_icon():
    """Ícono del programa en varios tamaños (QIcon elige el adecuado)."""
    from PySide6.QtGui import QIcon
    icon = QIcon()
    for name in ('logo_256.png', 'logo_512.png'):
        p = ASSETS_DIR / name
        if p.exists():
            icon.addFile(str(p))
    return icon


# Paletas: 'light' es la original (tomada de :root en AnsulCalc.html) y
# 'dark' es el modo oscuro. Todo color de la interfaz sale de aquí.
PALETTES = {
    'light': {
        'BG': '#f3f7fc', 'CARD': '#ffffff', 'CARD_BORDER': '#d3e1f0', 'TEXT': '#1e1e1e', 'MUTED': '#5a6272',
        'MUTED_2': '#98a2b3', 'BRAND_BLUE': '#0554a3', 'BRAND_BLUE_DARK': '#06407d', 'BRAND_BLUE_DARKER': '#033057',
        'ACCENT': '#0554a3', 'MENUBAR': '#0554a3', 'MENUBAR_HOVER': '#06407d', 'ALT_ROW': '#f7fafd',
        'GRID': '#eef2f8', 'SELECTION': '#dbe9fa', 'HEADER_BG': '#eaf1fb', 'BTN_DISABLED': '#b7c8dd',
        'BTN_DISABLED_TEXT': '#eef2f8', 'INPUT_BG': '#ffffff', 'INPUT_BORDER': '#c7d6e8',
        'INPUT_DISABLED_BG': '#eef2f6', 'SCROLL': '#b7c8dd', 'TOOLTIP': '#1e1e1e', 'HINT': '#888888',
        'INFO': '#555555', 'BANNER_BG': '#eef5ff', 'NOTE_BG': '#fff8e1', 'NOTE_TEXT': '#8a6d00',
        'OK_BORDER': '#2e7d32', 'OK_BG': '#f1f8f2', 'ERR_BORDER': '#b71c1c', 'ERR_BG': '#fdf1f1',
        'ERR_TEXT': '#7a1414', 'DANGER': '#b71c1c', 'DANGER_DARK': '#8f1414',
        # Diagrama del área protegida
        'DIAGRAM_FILL': '#e8f1fb', 'DIAGRAM_STROKE': '#0554a3', 'DIAGRAM_TEXT': '#5a6472', 'DIAGRAM_MUTED': '#98a2b3',
    },
    'dark': {
        'BG': '#14181e', 'CARD': '#1c222a', 'CARD_BORDER': '#2e3a48', 'TEXT': '#e4e8ee', 'MUTED': '#a3adba',
        'MUTED_2': '#7d8896', 'BRAND_BLUE': '#2a74c4', 'BRAND_BLUE_DARK': '#3584d6', 'BRAND_BLUE_DARKER': '#1f5fa6',
        'ACCENT': '#7ab6f2', 'MENUBAR': '#0f2f52', 'MENUBAR_HOVER': '#1d4a7a', 'ALT_ROW': '#20272f',
        'GRID': '#2a333e', 'SELECTION': '#244a73', 'HEADER_BG': '#232d3a', 'BTN_DISABLED': '#2f3a47',
        'BTN_DISABLED_TEXT': '#7d8896', 'INPUT_BG': '#11161c', 'INPUT_BORDER': '#3a4757',
        'INPUT_DISABLED_BG': '#1a1f26', 'SCROLL': '#3a4757', 'TOOLTIP': '#000000', 'HINT': '#8d97a5',
        'INFO': '#b3bcc8', 'BANNER_BG': '#16283d', 'NOTE_BG': '#2f2812', 'NOTE_TEXT': '#f0d58a',
        'OK_BORDER': '#3fa45a', 'OK_BG': '#15271a', 'ERR_BORDER': '#d9534f', 'ERR_BG': '#2c1717',
        'ERR_TEXT': '#f3c4c2', 'DANGER': '#c94040', 'DANGER_DARK': '#a83232',
        'DIAGRAM_FILL': '#1d3550', 'DIAGRAM_STROKE': '#7ab6f2', 'DIAGRAM_TEXT': '#b3bcc8', 'DIAGRAM_MUTED': '#7d8896',
    },
}

# Nombres anteriores (por compatibilidad con código que los importe)
BRAND_BLUE = PALETTES['light']['BRAND_BLUE']
BG = PALETTES['light']['BG']
TEXT = PALETTES['light']['TEXT']

_current = 'light'


def current_theme():
    return _current


def color(name):
    """Color de la paleta del tema activo (p. ej. color('DIAGRAM_FILL'))."""
    return PALETTES[_current][name]


def build_qss(theme='light'):
    return _QSS_TEMPLATE.format(**PALETTES[theme])


def apply_theme(app, theme):
    """Aplica el tema a toda la aplicación (funciona en vivo, sin reiniciar)."""
    global _current
    _current = theme if theme in PALETTES else 'light'
    app.setStyleSheet(build_qss(_current))
    for w in app.allWidgets():   # repintar los dibujos propios (diagrama)
        w.update()


def set_role(widget, role):
    """Cambia el 'rol' visual de un QLabel (ver los roles al final de la hoja
    de estilo) y lo vuelve a pintar con el estilo nuevo."""
    widget.setProperty('role', role)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


_QSS_TEMPLATE = """
QWidget {{
    background: {BG};
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background: {BG};
}}

QMenuBar {{
    background: {MENUBAR};
    color: white;
    padding: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
}}
QMenuBar::item:selected {{
    background: {MENUBAR_HOVER};
    border-radius: 4px;
}}
QMenu {{
    background: {CARD};
    border: 1px solid {CARD_BORDER};
    padding: 4px;
}}
QMenu::item {{
    padding: 5px 20px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {HEADER_BG};
    color: {ACCENT};
}}

QGroupBox {{
    background: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    margin-top: 16px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: {ACCENT};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
}}

QTreeWidget, QTableWidget, QListWidget {{
    background: {CARD};
    alternate-background-color: {ALT_ROW};
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    gridline-color: {GRID};
    selection-background-color: {SELECTION};
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background: {HEADER_BG};
    color: {ACCENT};
    border: none;
    border-bottom: 1px solid {CARD_BORDER};
    padding: 5px;
    font-weight: 600;
}}

QPushButton {{
    background: {BRAND_BLUE};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background: {BRAND_BLUE_DARK}; }}
QPushButton:pressed {{ background: {BRAND_BLUE_DARKER}; }}
QPushButton:disabled {{ background: {BTN_DISABLED}; color: {BTN_DISABLED_TEXT}; }}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: {INPUT_BG};
    border: 1px solid {INPUT_BORDER};
    border-radius: 6px;
    padding: 4px 6px;
    selection-background-color: {BRAND_BLUE};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {BRAND_BLUE};
}}
QLineEdit:disabled, QComboBox:disabled {{
    background: {INPUT_DISABLED_BG};
    color: {MUTED_2};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QCheckBox {{
    spacing: 6px;
}}

/* Textos sobre tarjetas: sin el fondo general detrás (se notaba en modo oscuro) */
QLabel, QCheckBox, QRadioButton {{
    background: transparent;
}}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {MUTED_2};
    border-radius: 3px;
    background: {INPUT_BG};
}}
QCheckBox::indicator:checked {{
    background: {BRAND_BLUE};
    border: 1px solid {BRAND_BLUE_DARKER};
}}
QCheckBox::indicator:disabled {{
    background: {INPUT_DISABLED_BG};
}}

QLabel[role="section-title"] {{
    color: {ACCENT};
    font-weight: 700;
    font-size: 16px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QAbstractScrollArea::corner {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 13px;
    margin: 2px 2px 2px 2px;
    border: none;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background: {SCROLL};
    min-height: 28px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BRAND_BLUE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 13px;
    margin: 2px 2px 2px 2px;
    border: none;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {SCROLL};
    min-width: 28px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {BRAND_BLUE};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}

QSplitter::handle {{
    background: {CARD_BORDER};
    border-radius: 3px;
}}

QToolTip {{
    background: {TOOLTIP};
    color: white;
    border: none;
    padding: 4px 6px;
}}

/* ---- Roles de texto (style.set_role(widget, ...)) ---- */
QLabel[role="hint"] {{ color: {HINT}; font-size: 11px; }}
QLabel[role="info"] {{ color: {INFO}; font-style: italic; }}
QLabel[role="footer"] {{ color: {HINT}; font-size: 11px; padding: 6px 10px; }}
QLabel[role="empty"] {{ color: {HINT}; font-size: 14px; }}
QLabel[role="title"] {{ font-size: 18px; font-weight: bold; }}
QLabel[role="brand"] {{ font-weight: bold; color: {ACCENT}; }}
QLabel[role="banner"] {{ background: {BANNER_BG}; color: {ACCENT}; padding: 6px; border-radius: 4px; }}
QLabel[role="note"] {{ background: {NOTE_BG}; color: {NOTE_TEXT}; padding: 6px; border-radius: 4px; }}
QLabel[role="result"] {{ padding: 8px; border: 1px solid {INPUT_BORDER}; border-radius: 4px; color: {HINT}; }}
QLabel[role="result-ok"] {{ padding: 8px; border: 1px solid {OK_BORDER}; background: {OK_BG}; border-radius: 4px; color: {TEXT}; }}
QLabel[role="result-error"] {{ padding: 8px; border: 1px solid {ERR_BORDER}; background: {ERR_BG}; border-radius: 4px; color: {ERR_TEXT}; }}
QTextEdit, QTextBrowser {{ background: {CARD}; color: {TEXT}; border: 1px solid {CARD_BORDER}; border-radius: 8px; }}
"""

STYLE_QSS = build_qss('light')
