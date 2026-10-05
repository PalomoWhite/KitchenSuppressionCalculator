# -*- coding: utf-8 -*-
"""
Tema visual (QSS) de la aplicación — puerto de la paleta y estilo de tarjetas
de AnsulCalc.html (variables :root, .card, .btn/.btn-primary/.btn-secondary/
.btn-danger, .topbar, .section-title, .field label) a Qt Style Sheets, para
que la versión de escritorio se vea como la herramienta web original.
"""

# Paleta tomada de :root en AnsulCalc.html
BRAND_BLUE = '#0554a3'
BRAND_BLUE_DARK = '#06407d'
BRAND_BLUE_DARKER = '#033057'
BG = '#f3f7fc'
CARD_BORDER = '#d3e1f0'
TEXT = '#1e1e1e'
MUTED = '#5a6272'
DANGER = '#b71c1c'
DANGER_DARK = '#8f1414'

STYLE_QSS = f"""
QWidget {{
    background: {BG};
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background: {BG};
}}

QMenuBar {{
    background: {BRAND_BLUE};
    color: white;
    padding: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
}}
QMenuBar::item:selected {{
    background: {BRAND_BLUE_DARK};
    border-radius: 4px;
}}
QMenu {{
    background: white;
    border: 1px solid {CARD_BORDER};
    padding: 4px;
}}
QMenu::item {{
    padding: 5px 20px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: #eaf1fb;
    color: {BRAND_BLUE};
}}

QGroupBox {{
    background: #ffffff;
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    margin-top: 16px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: {BRAND_BLUE};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
}}

QTreeWidget, QTableWidget, QListWidget {{
    background: #ffffff;
    alternate-background-color: #f7fafd;
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    gridline-color: #eef2f8;
    selection-background-color: #dbe9fa;
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background: #eaf1fb;
    color: {BRAND_BLUE};
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
QPushButton:disabled {{ background: #b7c8dd; color: #eef2f8; }}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: white;
    border: 1px solid #c7d6e8;
    border-radius: 6px;
    padding: 4px 6px;
    selection-background-color: {BRAND_BLUE};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {BRAND_BLUE};
}}
QLineEdit:disabled, QComboBox:disabled {{
    background: #eef2f6;
    color: #98a2b3;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QCheckBox {{
    spacing: 6px;
}}

QLabel[role="section-title"] {{
    color: {BRAND_BLUE};
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
    background: #b7c8dd;
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
    background: #b7c8dd;
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
    background: #1e1e1e;
    color: white;
    border: none;
    padding: 4px 6px;
}}
"""
