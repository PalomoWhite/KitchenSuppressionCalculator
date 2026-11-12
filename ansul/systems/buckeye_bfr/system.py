# -*- coding: utf-8 -*-
"""SystemDef de Buckeye Kitchen Mister (BFR-TM Rev. 6)."""
from ..base import SystemDef
from . import data as D
from . import engine as E
from . import category_defs as CD
from ...i18n import tr


class BuckeyeBFR(SystemDef):
    key = 'buckeye_bfr'
    label = tr('Buckeye Kitchen Mister')
    short = tr('Buckeye')
    flow_label = tr('Flow points')
    report_subtitle = tr('Sistema Buckeye Kitchen Mister (BFR) — manual BFR-TM Rev. 6')
    disclaimer = D.PDF_DISCLAIMER
    disclaimer_short = (tr('Esta herramienta es una ayuda de diseño preliminar basada en el manual Buckeye Kitchen '
                           'Mister (BFR-TM Rev. 6). El diseño final debe ser verificado por un distribuidor/diseñador '
                           'autorizado Buckeye, conforme a NFPA 17A y los códigos locales aplicables.'))

    supports_cylinder_choice = True

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

    def diagram_spec(self, category, values):
        return CD.diagram_spec(category, values) or ('none',)

    def nozzle_columns(self):
        return [tr('Boquilla'), tr('Color'), tr('No. de parte'), tr('Cantidad')]

    def nozzle_row(self, code, qty):
        n = D.NOZZLES.get(code, {})
        return [code, n.get('color', '—'), n.get('partNo', '—'), str(qty)]

    def kitchen_summary(self, kitchen):
        return E.kitchen_summary(kitchen)

    def project_summary(self, project):
        return E.project_summary(project)

    def summary_rows(self, s):
        rows = [(tr('Flow points totales del sistema'), E._fmt(s['totalFlow']))]
        chosen = s.get('chosen')
        if chosen:
            for size, n in sorted(s['cylinderCounts'].items(), reverse=True):
                c = D.CYLINDERS[size]
                rows.append((tr('Cilindro {0} (No. de parte {1}, soporte {2})').format(c['model'], c['partNo'], c['bracket']), str(n)))
            rows.append((tr('Capacidad de los cilindros (flow points)'), tr('{0} (sobran {1})').format(chosen['capacity'], chosen['surplus'])))
            for size in sorted(s['cylinderCounts'], reverse=True):
                c = D.CYLINDERS[size]
                txt = tr('{0} mL total, {1} mL entre boquillas, {2} codos').format(c['maxPipeMl'], c['maxPipeBetweenNozzlesMl'], c['maxElbows'])
                if c.get('maxPipe38Ml'):
                    txt += tr(' (máx. {0} mL en 3/8 in)').format(c['maxPipe38Ml'])
                rows.append((tr('Tubería máx. por {0} (p. 3-13)').format(c['model']), txt))
            if len(s['combos']) > 1:
                rows.append((tr('Otras combinaciones válidas'), str(len(s['combos']) - 1)))
        else:
            rows.append((tr('Cilindros'), '—'))
        return rows

    def summary_notes(self, s):
        return list(s.get('notes') or [])

    def containers_short(self, s):
        return E.combo_label(s['chosen']['cylinders']) if s.get('chosen') else '—'

    def project_rows(self, ps):
        rows = [(tr('Flow points totales del proyecto'), E._fmt(ps['totalFlow'])),
                (tr('Cilindros totales a instalar'), str(ps['totalCylinders']))]
        for size, n in sorted(ps['cylinderCounts'].items(), reverse=True):
            rows.append((f"  {D.CYLINDERS[size]['model']}", str(n)))
        return rows

    # Exclusivo de Buckeye: lista de combinaciones para el selector de la UI
    def cylinder_options(self, summary):
        return [(E.combo_label(c['cylinders']) + tr('  —  {0} FP (sobran {1})').format(c['capacity'], c['surplus']), c['cylinders'])
                for c in summary.get('combos') or []]


SYSTEM = BuckeyeBFR()
