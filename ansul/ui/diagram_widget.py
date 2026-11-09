# -*- coding: utf-8 -*-
"""
Diagrama en vivo del área protegida del equipo — versión en QPainter del
mismo concepto que rectDiagramSVG / circleDiagramSVG / nozzleIconSVG /
equipmentAreaDiagramHTML de AnsulCalc.html: a medida que el usuario captura
las medidas, se dibuja un rectángulo o círculo a escala con sus dimensiones,
usando la misma paleta azul de la app (relleno #e8f1fb, trazo #0554a3).
"""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QWidget

_FILL = QColor('#e8f1fb')
_STROKE = QColor('#0554a3')
_TEXT = QColor('#5a6472')
_MUTED = QColor('#98a2b3')

# Categoría -> (ancho_key, fondo_key, unidad) para las que se dibujan como
# rectángulo. Para 'fryer' se sustituye por overallL/overallD cuando el
# equipo tiene escurridor (dripboard).
_RECT_CATEGORIES = {
    'fryer': ('frypotL', 'frypotD', 'in'),
    'tiltskillet': ('d1', 'd2', 'in'),
    'range': ('d1', 'd2', 'in'),
    'griddle': ('d1', 'd2', 'in'),
    'grill': ('d1', 'd2', 'in'),
    'naturalcharcoal': ('d1', 'd2', 'in'),
    'woodgrill': ('d1', 'd2', 'in'),
    'robata': ('d1', 'd2', 'in'),
    'chainbroiler': ('width', 'length', 'in'),
    'uprightbroiler': ('width', 'length', 'in'),
    'salamander': ('width', 'length', 'in'),
    'plenum': ('widthM', 'lengthM', 'm'),
}
# Categoría -> (diámetro_key, unidad) para las que se dibujan como círculo.
_CIRCLE_CATEGORIES = {
    'wok': ('diam', 'in'),
}


def _f(v):
    try:
        n = float(v)
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def _fmt(n):
    if n is None:
        return '—'
    if n == int(n):
        return str(int(n))
    return f'{n:.2f}'.rstrip('0').rstrip('.')


class EquipmentDiagramWidget(QWidget):
    """Widget rectangular que dibuja, a escala, la forma y dimensiones del
    equipo capturado en el formulario. Se actualiza llamando a
    update_diagram(category, values, catalog_ref) cada vez que cambian los
    datos (ver EquipmentDialog._recompute)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(170)
        self._mode = None   # 'rect' | 'circle' | None
        self._dims = None
        self._unit = 'in'

    def update_diagram(self, category, values, catalog_ref=None, system=None):
        self._mode, self._dims = None, None

        # Marcas con su propio diagrama (Buckeye): la marca dice qué dibujar.
        spec = system.diagram_spec(category, values) if system is not None else None
        if spec is not None:
            if spec[0] == 'rect':
                self._mode, self._dims, self._unit = 'rect', (spec[1], spec[2]), spec[3]
            elif spec[0] == 'circle':
                self._mode, self._dims, self._unit = 'circle', (spec[1],), spec[2]
            self.update()
            return

        # Caso especial: el equipo viene de catálogo con superficie fija.
        if catalog_ref and _f(catalog_ref.get('surfaceW')) and _f(catalog_ref.get('surfaceD')):
            self._mode = 'rect'
            self._dims = (_f(catalog_ref.get('surfaceW')), _f(catalog_ref.get('surfaceD')))
            self._unit = 'in'
            self.update()
            return

        if category == 'duct':
            if values.get('round'):
                d = _f(values.get('diameter'))
                if d:
                    self._mode, self._dims, self._unit = 'circle', (d,), 'in'
            else:
                a, b = _f(values.get('sideA')), _f(values.get('sideB'))
                if a and b:
                    self._mode, self._dims, self._unit = 'rect', (a, b), 'in'
            self.update()
            return

        if category in _CIRCLE_CATEGORIES:
            key, unit = _CIRCLE_CATEGORIES[category]
            d = _f(values.get(key))
            if d:
                self._mode, self._dims, self._unit = 'circle', (d,), unit
            self.update()
            return

        if category in _RECT_CATEGORIES:
            wk, hk, unit = _RECT_CATEGORIES[category]
            w, h = _f(values.get(wk)), _f(values.get(hk))
            if category == 'fryer' and values.get('hasDripboard'):
                w2, h2 = _f(values.get('overallL')), _f(values.get('overallD'))
                if w2 and h2:
                    w, h = w2, h2
            if w and h:
                self._mode, self._dims, self._unit = 'rect', (w, h), unit
            self.update()
            return

        self.update()

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        try:
            rect = self.rect().adjusted(12, 10, -12, -10)
            if not self._mode or not self._dims:
                painter.setPen(QPen(_MUTED))
                font = QFont()
                font.setPointSize(9)
                painter.setFont(font)
                painter.drawText(self.rect(), Qt.AlignCenter,
                                  'Capture las medidas para ver\nel diagrama del área protegida.')
                return
            if self._mode == 'rect':
                self._draw_rect(painter, rect, *self._dims)
            else:
                self._draw_circle(painter, rect, self._dims[0])
        finally:
            painter.end()

    def _draw_rect(self, painter, rect, w, h):
        avail_w, avail_h = rect.width(), rect.height() - 22
        if avail_h <= 0 or not w or not h:
            return
        scale = min(avail_w / w, avail_h / h)
        draw_w, draw_h = w * scale, h * scale
        x = rect.left() + (rect.width() - draw_w) / 2
        y = rect.top() + (avail_h - draw_h) / 2
        box = QRectF(x, y, draw_w, draw_h)
        painter.setBrush(QBrush(_FILL))
        painter.setPen(QPen(_STROKE, 2))
        painter.drawRoundedRect(box, 4, 4)
        self._draw_caption(painter, rect, box.bottom(), f'{_fmt(w)} × {_fmt(h)} {self._unit}')

    def _draw_circle(self, painter, rect, d):
        avail = min(rect.width(), rect.height() - 22)
        if avail <= 0 or not d:
            return
        scale = avail / d
        size = d * scale
        x = rect.left() + (rect.width() - size) / 2
        y = rect.top() + (rect.height() - 22 - size) / 2
        box = QRectF(x, y, size, size)
        painter.setBrush(QBrush(_FILL))
        painter.setPen(QPen(_STROKE, 2))
        painter.drawEllipse(box)
        self._draw_caption(painter, rect, box.bottom(), f'Ø {_fmt(d)} {self._unit}')

    def _draw_caption(self, painter, rect, y, text):
        painter.setPen(QPen(_TEXT))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(QRectF(rect.left(), y + 4, rect.width(), 16), Qt.AlignHCenter, text)
