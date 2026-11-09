# -*- coding: utf-8 -*-
"""
Referencia rápida Buckeye Kitchen Mister (BFR-TM Rev. 6): boquillas,
cilindros, coberturas y tubería. Solo consulta — no participa en cálculos.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                                QHeaderView, QDialogButtonBox, QTabWidget, QWidget, QTextEdit)

from ..systems.buckeye_bfr import data as BD


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
        self.setWindowTitle(f'Referencia — Buckeye Kitchen Mister ({BD.MANUAL})')
        self.setMinimumSize(820, 520)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        nozzles = _table(['Boquilla', 'Flow points', 'Color de banda', 'No. de parte', 'Descripción'],
                         [[c, n['flow'], n['color'], n['partNo'], n['desc']] for c, n in BD.NOZZLES.items()])
        tabs.addTab(*_tab('Boquillas', ['Boquillas (p. 2-9); números de parte (p. 2-11).', nozzles]))

        cyl = _table(['Cilindro', 'Flow points', 'No. de parte', 'Soporte', 'Peso', 'Tubería máx. (mL)',
                      'Máx. entre 2 boquillas (mL)', 'Codos máx.'],
                     [[c['model'], c['flow'], c['partNo'], c['bracket'], c['weight'],
                       f"{c['maxPipeMl']}" + (f" ({c['maxPipe38Ml']} en 3/8 in)" if c.get('maxPipe38Ml') else ''),
                       c['maxPipeBetweenNozzlesMl'], c['maxElbows']] for c in BD.CYLINDERS.values()])
        tabs.addTab(*_tab('Cilindros', [f'Cilindros (p. 2-1, p. 2-10) y tubería máxima por cilindro (p. 3-13). '
                                        f'Carga: {BD.CYLINDER_CHARGE}.', cyl]))

        rows = (_cov(BD.RANGE_OPTIONS, 'Estufa') + _cov(BD.RANGE_GRIDDLE_OPTIONS, 'Estufa-plancha')
                + _cov(BD.GRIDDLE_OPTIONS, 'Plancha') + _cov(BD.FRYER_OPTIONS, 'Freidora')
                + _cov(BD.TILT_SKILLET_OPTIONS, 'Sartén de volteo')
                + _cov(list(BD.CHARBROILER_OPTIONS.values()), 'Asador') + _cov([BD.UPRIGHT_BROILER], 'Asador vertical'))
        rows.append(['Wok', f"Ø {BD.WOK['diamMin']}–{BD.WOK['diamMax']}", BD.WOK['nozzle'], 1,
                     f"{BD.WOK['hmin']}–{BD.WOK['hmax']} (desde el fondo)", BD.WOK['page']])
        for d in BD.DUCT_OPTIONS:
            rows.append([f"Ducto (perímetro ≤ {d['maxPerimeter']}, lado ≤ {d['maxSide']}; redondo ≤ "
                         f"{d['maxCircumference']} circ. / Ø{d['maxDiameter']})", '—', d['nozzle'],
                         BD.NOZZLES[d['nozzle']]['flow'], d['depth'], d['page']])
        rows.append(['Pleno (por boquilla)', f"{BD.PLENUM['maxLengthFt']} ft × {BD.PLENUM['maxWidthFt']} ft",
                     BD.PLENUM['nozzle'], 1, '1/3 de la altura', BD.PLENUM['page']])
        cov = _table(['Aplicación', 'Cobertura ancho × fondo (in)', 'Boquilla', 'FP', 'Altura (in)', 'Pág.'], rows)
        tabs.addTab(*_tab('Coberturas', [
            'Coberturas por boquilla (tabla resumen p. 3-12 y páginas de detalle). Si el equipo es más grande, se '
            f'divide en módulos iguales (p. 3-11). Freidoras: máximo {BD.FRYER_MAX_MODULAR_AREA} in² modularizable.',
            cov]))

        text = QTextEdit()
        text.setReadOnly(True)
        html = ('<h3>Requisitos generales (p. 3-13)</h3><ol>'
                + ''.join(f'<li style="margin-bottom:6px">{n}</li>' for n in BD.PIPING_NOTES) + '</ol>'
                + '<h3>Requisitos mínimos — solo con wok, freidora o estufa (p. 3-13)</h3><ol>'
                + ''.join(f'<li style="margin-bottom:6px">{n}</li>' for n in BD.MIN_PIPING_NOTES) + '</ol>')
        text.setHtml(html)
        tabs.addTab(*_tab('Tubería', [text]))

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
