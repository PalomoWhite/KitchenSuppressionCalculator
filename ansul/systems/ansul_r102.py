# -*- coding: utf-8 -*-
"""
Adaptador ANSUL R-102: expone los módulos existentes (ansul/data.py,
engine.py, category_defs.py) con la interfaz SystemDef. No cambia ningún
cálculo — solo reúne en un lugar lo que la interfaz y el PDF ya usaban.
"""
from .. import data as D
from .. import engine as E
from .. import category_defs as CD
from .base import SystemDef


class AnsulR102(SystemDef):
    key = 'ansul_r102'
    label = 'ANSUL R-102'
    short = 'ANSUL'
    flow_label = 'Flow number'
    report_subtitle = 'Sistema ANSUL(R) R-102'
    disclaimer = D.PDF_DISCLAIMER
    disclaimer_short = ('Esta herramienta es una ayuda de diseño preliminar basada en el manual ANSUL(R) R-102. '
                        'El diseño final debe ser verificado y sellado por un diseñador certificado ANSUL R-102, '
                        'conforme a NFPA 17A y los códigos locales aplicables.')

    supports_catalog = True
    supports_tank_override = True

    category_order = D.CATEGORY_ORDER
    category_labels = D.CATEGORY_LABELS
    category_defs = CD.CATEGORY_DEFS

    def has_required_inputs(self, category, values):
        return CD.has_required_inputs(category, values)

    def category_display_label(self, item):
        return CD.category_display_label(item)

    def dimensions_display(self, item):
        return CD.dimensions_display(item)

    def depth_display(self, item):
        return CD.depth_display(item)

    def nozzle_row(self, code, qty):
        return [code, D.NOZZLES.get(code, {}).get('partNo', '—'), str(qty)]

    def kitchen_summary(self, kitchen):
        return E.kitchen_summary(kitchen)

    def project_summary(self, project):
        return E.project_summary(project)

    def summary_rows(self, summary):
        rows = [('Capacidad total de flujo del sistema (flow number)', E.fmt_num(summary['totalFlow']))]
        tanks = summary['tanks']
        if tanks.get('manual'):
            rows.append(('Selección de tanques', 'Manual (elegida por el usuario)'))
        if tanks.get('tankCount'):
            counts = E.tank_counts(tanks['tanks'])
            for g in sorted(counts.keys(), reverse=True):
                rows.append((f'Tanque de {g} gal', str(counts[g])))
        rows.append(('Galonaje total de agente', f"{E.fmt_num(tanks.get('totalGallons'))} gal"))
        rows.append(('Cartucho — opción nitrógeno (N2)', tanks.get('n2') or '—'))
        rows.append(('Cartucho — opción CO2 (alternativa al N2, no ambos)', tanks.get('co2') or '—'))
        return rows

    def summary_notes(self, summary):
        note = summary['tanks'].get('note')
        return [note] if note else []

    def containers_short(self, summary):
        t = summary['tanks']
        return f"{t['tankCount']} ({E.fmt_num(t['totalGallons'])} gal)" if t.get('tankCount') else '—'

    def project_rows(self, ps):
        return [
            ('Capacidad total de flujo del proyecto (flow number)', E.fmt_num(ps['totalFlow'])),
            ('Tanques totales a instalar', str(ps['totalTanks'])),
            ('Galonaje total de agente', f"{E.fmt_num(ps['totalGallons'])} gal"),
        ]


SYSTEM = AnsulR102()
