# -*- coding: utf-8 -*-
"""
Ventana de referencia rápida: requisitos de tubería de distribución por
tamaño de sistema y notas generales de tubería, tomados de la Hoja Resumen
ANSUL F-2015158-01_LAS (páginas 3-4) y el manual R-102. Es contenido de
consulta — no participa en ningún cálculo.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                                QHeaderView, QDialogButtonBox, QTabWidget, QWidget, QTextEdit)

from .. import data as D

PIPING_COLS = [
    ('system', 'Sistema'), ('flowMax', 'Flujo máx. (línea supl.)'),
    ('supplyLenFt', 'Supl. long. máx (ft)'), ('supplyElevFt', 'Supl. elev. máx (ft)'),
    ('supplyElbows90', 'Supl. codos 90°'), ('supplyTees', 'Supl. tubos T'),
    ('branchLenFt', 'Ramal long. máx (ft)'), ('branchElevFt', 'Ramal elev. máx (ft)'),
    ('branchElbows90', 'Ramal codos 90°'), ('branchTees', 'Ramal tubos T'), ('branchFlowMax', 'Ramal flujo máx'),
    ('ApplianceBranchLenFt', 'Ramal aparato long. máx (ft)'), ('ApplianceBranchFlowMax', 'Ramal aparato flujo máx'),
]


class ReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Referencia — Requisitos de tubería R-102')
        self.setMinimumSize(760, 480)
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # ---- Tabla de requisitos de tubería por tamaño de sistema ----
        piping_tab = QWidget()
        pl = QVBoxLayout(piping_tab)
        note = QLabel('Basado en la Hoja Resumen ANSUL F-2015158-01_LAS (pág. 3-4). Consulte el manual R-102 '
                       'completo para excepciones e instrucciones especiales por sistema.')
        note.setWordWrap(True)
        pl.addWidget(note)

        table = QTableWidget(len(D.PIPING_REQUIREMENTS), len(PIPING_COLS))
        table.setHorizontalHeaderLabels([label for _, label in PIPING_COLS])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for row, sysreq in enumerate(D.PIPING_REQUIREMENTS):
            for col, (key, _label) in enumerate(PIPING_COLS):
                table.setItem(row, col, QTableWidgetItem(str(sysreq.get(key, '—'))))
        table.resizeColumnsToContents()
        pl.addWidget(table)
        tabs.addTab(piping_tab, 'Tuberías por sistema')

        # ---- Notas generales ----
        notes_tab = QWidget()
        nl = QVBoxLayout(notes_tab)
        text = QTextEdit()
        text.setReadOnly(True)
        html = '<ol>' + ''.join(f'<li style="margin-bottom:8px">{n}</li>' for n in D.PIPING_GENERAL_NOTES) + '</ol>'
        text.setHtml(html)
        nl.addWidget(text)
        tabs.addTab(notes_tab, 'Requisitos generales de tubería')

        # ---- Tabla de boquillas ----
        nozzle_tab = QWidget()
        nzl = QVBoxLayout(nozzle_tab)
        nozzle_table = QTableWidget(len(D.NOZZLES), 3)
        nozzle_table.setHorizontalHeaderLabels(['Boquilla', 'No. de parte', 'Flow number'])
        for row, (code, info) in enumerate(sorted(D.NOZZLES.items())):
            nozzle_table.setItem(row, 0, QTableWidgetItem(code))
            nozzle_table.setItem(row, 1, QTableWidgetItem(info['partNo']))
            nozzle_table.setItem(row, 2, QTableWidgetItem(str(info['flow'])))
        nozzle_table.resizeColumnsToContents()
        nzl.addWidget(QLabel('Tabla 3-2: Nozzle Identification Chart (manual R-102, Sección 3, pág. 3-5)'))
        nzl.addWidget(nozzle_table)
        tabs.addTab(nozzle_tab, 'Catálogo de boquillas')

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
