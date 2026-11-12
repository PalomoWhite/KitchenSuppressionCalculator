# -*- coding: utf-8 -*-
"""
Referencia rápida Buckeye Kitchen Mister (BFR-TM Rev. 6): boquillas,
cilindros, coberturas y tubería. Solo consulta — no participa en cálculos.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                                QHeaderView, QDialogButtonBox, QTabWidget, QWidget, QTextEdit)

from ..systems.buckeye_bfr import data as BD
from ..i18n import tr


def _table(headers, rows):
    t = QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            t.setItem(r, c, QTableWidgetItem(str(v)))
    t.resizeColumnsToContents()
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    t.horizontalHeader().setStretchLastSection(True)
    return t


def _tab(title, widgets):
    w = QWidget()
    lay = QVBoxLayout(w)
    for x in widgets:
        if isinstance(x, str):
            lbl = QLabel(x)
            lbl.setWordWrap(True)
            lay.addWidget(lbl)
        else:
            lay.addWidget(x)
    return w, title


def _cov(opts, label):
    return [[label + ' — ' + o['tag'], f"{o['w']} × {o['d']}", o['nozzle'], BD.NOZZLES[o['nozzle']]['flow'],
             f"{o['hmin']}–{o['hmax']}" if 'hmin' in o else o.get('height', '—'), o['page']] for o in opts]


class BuckeyeReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Referencia — Buckeye Kitchen Mister ({0})').format(BD.MANUAL))
        self.setMinimumSize(820, 520)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        nozzles = _table([tr('Boquilla'), tr('Flow points'), tr('Color de banda'), tr('No. de parte'), tr('Descripción')],
                         [[c, n['flow'], n['color'], n['partNo'], n['desc']] for c, n in BD.NOZZLES.items()])
        tabs.addTab(*_tab(tr('Boquillas'), [tr('Boquillas (p. 2-9); números de parte (p. 2-11).'), nozzles]))

        cyl = _table([tr('Cilindro'), tr('Flow points'), tr('No. de parte'), tr('Soporte'), tr('Peso'), tr('Tubería máx. (mL)'),
                      tr('Máx. entre 2 boquillas (mL)'), tr('Codos máx.')],
                     [[c['model'], c['flow'], c['partNo'], c['bracket'], c['weight'],
                       f"{c['maxPipeMl']}" + (tr(' ({0} en 3/8 in)').format(c['maxPipe38Ml']) if c.get('maxPipe38Ml') else ''),
                       c['maxPipeBetweenNozzlesMl'], c['maxElbows']] for c in BD.CYLINDERS.values()])
        tabs.addTab(*_tab(tr('Cilindros'), [tr('Cilindros (p. 2-1, p. 2-10) y tubería máxima por cilindro (p. 3-13). Carga: {0}.').format(BD.CYLINDER_CHARGE), cyl]))

        rows = (_cov(BD.RANGE_OPTIONS, tr('Estufa')) + _cov(BD.RANGE_GRIDDLE_OPTIONS, 'Estufa-plancha')
                + _cov(BD.GRIDDLE_OPTIONS, tr('Plancha')) + _cov(BD.FRYER_OPTIONS, tr('Freidora'))
                + _cov(BD.TILT_SKILLET_OPTIONS, tr('Sartén de volteo'))
                + _cov(list(BD.CHARBROILER_OPTIONS.values()), tr('Asador')) + _cov([BD.UPRIGHT_BROILER], tr('Asador vertical')))
        rows.append([tr('Wok'), f"Ø {BD.WOK['diamMin']}–{BD.WOK['diamMax']}", BD.WOK['nozzle'], 1,
                     tr('{0}–{1} (desde el fondo)').format(BD.WOK['hmin'], BD.WOK['hmax']), BD.WOK['page']])
        for d in BD.DUCT_OPTIONS:
            rows.append([tr('Ducto (perímetro ≤ {0}, lado ≤ {1}; redondo ≤ {2} circ. / Ø{3})').format(d['maxPerimeter'], d['maxSide'], d['maxCircumference'], d['maxDiameter']), '—', d['nozzle'],
                         BD.NOZZLES[d['nozzle']]['flow'], d['depth'], d['page']])
        rows.append([tr('Pleno (por boquilla)'), tr('{0} ft × {1} ft').format(BD.PLENUM['maxLengthFt'], BD.PLENUM['maxWidthFt']),
                     BD.PLENUM['nozzle'], 1, tr('1/3 de la altura'), BD.PLENUM['page']])
        cov = _table([tr('Aplicación'), tr('Cobertura ancho × fondo (in)'), tr('Boquilla'), 'FP', tr('Altura (in)'), tr('Pág.')], rows)
        tabs.addTab(*_tab(tr('Coberturas'), [
            tr('Coberturas por boquilla (tabla resumen p. 3-12 y páginas de detalle). Si el equipo es más '
               'grande, se divide en módulos iguales (p. 3-11). Freidoras: máximo {0} in² modularizable.').format(BD.FRYER_MAX_MODULAR_AREA),
            cov]))

        text = QTextEdit()
        text.setReadOnly(True)
        html = (tr('<h3>Requisitos generales (p. 3-13)</h3><ol>')
                + ''.join(f'<li style="margin-bottom:6px">{n}</li>' for n in BD.PIPING_NOTES) + '</ol>'
                + tr('<h3>Requisitos mínimos — solo con wok, freidora o estufa (p. 3-13)</h3><ol>')
                + ''.join(f'<li style="margin-bottom:6px">{n}</li>' for n in BD.MIN_PIPING_NOTES) + '</ol>')
        text.setHtml(html)
        tabs.addTab(*_tab(tr('Tubería'), [text]))

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
