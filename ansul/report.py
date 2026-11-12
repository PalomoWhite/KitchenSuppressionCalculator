# -*- coding: utf-8 -*-
"""
Generación de reportes PDF — equivalente a buildKitchenReportPdf /
buildProjectReportPdf de AnsulCalc.html, usando reportlab en vez de jsPDF.
El contenido y el orden de las secciones son los mismos que en el HTML.
"""
import re
import unicodedata

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak)

from . import engine as E
from . import systems
from .store import today_iso
from .i18n import tr

MARGIN = 0.64 * inch  # ~46pt, igual que PDF_MARGIN en el HTML

_STYLE_TITLE = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#0f0f0f'),
                               spaceAfter=4)
_STYLE_SUBTITLE = ParagraphStyle('subtitle', fontName='Helvetica-Bold', fontSize=10.5, textColor=colors.HexColor('#5a6272'),
                                  spaceAfter=8)
_STYLE_SECTION = ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=11.5, textColor=colors.HexColor('#0554a3'),
                                 spaceBefore=10, spaceAfter=6, borderColor=colors.HexColor('#0554a3'),
                                 borderWidth=0, borderPadding=0)
_STYLE_SUBSECTION = ParagraphStyle('subsection', fontName='Helvetica-Bold', fontSize=11.5,
                                    textColor=colors.HexColor('#0554a3'), spaceBefore=8, spaceAfter=6)
_STYLE_PARA = ParagraphStyle('para', fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#1e1e1e'),
                              spaceAfter=6, leading=12)
_STYLE_DIM = ParagraphStyle('dim', fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#6e6e6e'),
                             spaceAfter=4, leading=10)
_STYLE_NOTE = ParagraphStyle('note', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#1e1e1e'),
                              spaceAfter=6, leading=12)


def pdf_sanitize_filename(s):
    s = str(s or 'reporte')
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-zA-Z0-9._-]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or 'reporte'


def _table(rows, col_widths, header=None, num_cols=None):
    """rows: lista de listas de celdas (str). header: lista de encabezados
    o None. num_cols: índices (0-based) de columnas alineadas a la derecha."""
    num_cols = num_cols or set()
    data = []
    if header:
        data.append(header)
    data.extend(rows)
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#282828')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, -1), (-1, -1), 0.6, colors.HexColor('#dcdcdc')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for c in num_cols:
        style.append(('ALIGN', (c, 0), (c, -1), 'RIGHT'))
    if header:
        style += [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e1e1e')),
            ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor('#b4b4b4')),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ]
    t.setStyle(TableStyle(style))
    return t


def _nozzle_breakdown_table(system, nozzle_totals, total_width):
    codes = sorted(nozzle_totals.keys())
    header = [tr('Boquilla (modelo)')] + list(system.nozzle_columns())[1:]
    ncols = len(header)
    if not codes:
        rows = [[tr('Sin riesgos calculados')] + ['—'] * (ncols - 1)]
    else:
        rows = [system.nozzle_row(c, nozzle_totals[c]) for c in codes]
    weights = [1.6, 1.3, 1.0] if ncols == 3 else [1.3, 1.0, 1.2, 0.8]
    widths = [total_width * w / sum(weights) for w in weights]
    return _table(rows, widths, header=header, num_cols={ncols - 1})


def _summary_rows(system, summary):
    return [list(r) for r in system.summary_rows(summary)]


def _equipment_rows(system, kitchen):
    rows = []
    for item in kitchen.get('equipment', []):
        r = item.get('result') or {}
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (r.get('nozzles') or [])) or '—'
        brand_model = ' '.join(x for x in [item.get('brand'), item.get('model')] if x) or '—'
        rows.append([system.category_display_label(item), brand_model, nozz_txt, E.fmt_num(r.get('flowNumber'))])
    return rows


def _flow_header(system):
    return tr('Flow pts') if system.flow_label == 'Flow points' else tr('Flow')


def _header_block(story, title, subtitle, project_name, extra_line, responsible, date, quote_number=''):
    story.append(Paragraph(title, _STYLE_TITLE))
    story.append(Paragraph(subtitle, _STYLE_SUBTITLE))
    story.append(Paragraph(extra_line, _STYLE_PARA))
    resp_line = tr('Responsable: {0}&nbsp;&nbsp;&nbsp;&nbsp;Fecha: {1}').format(responsible or '—', date or '—')
    if quote_number:
        resp_line += tr('&nbsp;&nbsp;&nbsp;&nbsp;No. de cotización: {0}').format(quote_number)
    story.append(Paragraph(resp_line, _STYLE_PARA))
    story.append(Spacer(1, 6))


def _detail_block(story, system, kitchen):
    """Buckeye: altura, colocación y página del manual de cada riesgo (en
    ANSUL el reporte se queda como estaba)."""
    if system.key != 'buckeye_bfr':
        return
    items = [i for i in kitchen.get('equipment', []) if i.get('result')]
    if not items:
        return
    story.append(Paragraph(tr('Detalle de protección por riesgo — {0}').format(_esc(kitchen['name'])), _STYLE_SECTION))
    for i in items:
        r = i['result']
        dims = system.dimensions_display(i)
        head = system.category_display_label(i) + (f' ({dims})' if dims else '')
        story.append(Paragraph(tr('<b>{0}</b> — altura: {1}<br/>{2}').format(_esc(head), _esc(r.get('heightRange', '—')), _esc(r.get('detail', ''))), _STYLE_NOTE))


def _esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_kitchen_report_pdf(project, kitchen, out_path, responsible='', date=None, quote_number=''):
    date = date or today_iso()
    system = systems.for_project(project)
    s = system.kitchen_summary(kitchen)
    total_width = letter[0] - 2 * MARGIN

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                             leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    _header_block(story, tr('Ansul Flow Calculator — Reporte de cálculo'), system.report_subtitle,
                  project['name'], tr('Proyecto: {0}&nbsp;&nbsp;&nbsp;&nbsp;Sistema: {1}').format(project['name'], kitchen['name']),
                  responsible, date, quote_number)

    story.append(Paragraph(tr('Riesgos, ductos y plenos'), _STYLE_SECTION))
    eq_rows = _equipment_rows(system, kitchen)
    widths = [total_width * w / 6 for w in (1.9, 2.1, 1.3, 0.7)]
    story.append(_table(eq_rows or [[tr('Sin riesgos'), '—', '—', '—']], widths,
                         header=[tr('Tipo'), tr('Marca / Modelo'), tr('Boquillas'), _flow_header(system)], num_cols={3}))
    story.append(Spacer(1, 8))

    story.append(Paragraph(tr('Resumen de materiales — {0}').format(kitchen['name']), _STYLE_SECTION))
    widths2 = [total_width * 3 / 4, total_width * 1 / 4]
    story.append(_table(_summary_rows(system, s), widths2, header=[tr('Concepto'), tr('Cantidad')], num_cols={1}))
    for note in system.summary_notes(s):
        story.append(Spacer(1, 4))
        story.append(Paragraph(note, _STYLE_NOTE))
    story.append(Spacer(1, 8))

    story.append(Paragraph(tr('Boquillas requeridas — {0}').format(kitchen['name']), _STYLE_SECTION))
    story.append(_nozzle_breakdown_table(system, s['nozzleTotals'], total_width))
    _detail_block(story, system, kitchen)
    story.append(Spacer(1, 14))
    story.append(Paragraph(system.disclaimer, _STYLE_DIM))

    doc.build(story)
    return out_path


def build_project_report_pdf(project, out_path, responsible='', date=None, quote_number=''):
    date = date or today_iso()
    system = systems.for_project(project)
    ps = system.project_summary(project)
    total_width = letter[0] - 2 * MARGIN

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                             leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    _header_block(story, tr('Ansul Flow Calculator — Reporte general del proyecto'), system.report_subtitle,
                  project['name'], tr('Proyecto: {0}&nbsp;&nbsp;&nbsp;&nbsp;Sistemas: {1}').format(project['name'], len(project['kitchens'])),
                  responsible, date, quote_number)

    story.append(Paragraph(tr('Resumen general de materiales (todos los sistemas)'), _STYLE_SECTION))
    overall_rows = [[tr('Sistemas'), str(len(project['kitchens']))]] + [list(r) for r in system.project_rows(ps)]
    widths2 = [total_width * 3 / 4, total_width * 1 / 4]
    story.append(_table(overall_rows, widths2, header=[tr('Concepto'), tr('Cantidad')], num_cols={1}))
    story.append(Spacer(1, 6))
    story.append(_nozzle_breakdown_table(system, ps['nozzleTotals'], total_width))
    story.append(Spacer(1, 10))

    story.append(Paragraph(tr('Detalle por sistema'), _STYLE_SECTION))
    widths = [total_width * w / 6 for w in (1.9, 2.1, 1.3, 0.7)]
    for entry in ps['kitchenSummaries']:
        kitchen, summary = entry['kitchen'], entry['summary']
        story.append(Paragraph(kitchen['name'], _STYLE_SUBSECTION))
        eq_rows = _equipment_rows(system, kitchen)
        story.append(_table(eq_rows or [[tr('Sin riesgos'), '—', '—', '—']], widths,
                             header=[tr('Tipo'), tr('Marca / Modelo'), tr('Boquillas'), _flow_header(system)], num_cols={3}))
        story.append(Spacer(1, 4))
        story.append(_table(_summary_rows(system, summary), widths2, header=[tr('Concepto'), tr('Cantidad')], num_cols={1}))
        for note in system.summary_notes(summary):
            story.append(Spacer(1, 3))
            story.append(Paragraph(note, _STYLE_NOTE))
        story.append(Spacer(1, 4))
        story.append(_nozzle_breakdown_table(system, summary['nozzleTotals'], total_width))
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 8))
    story.append(Paragraph(system.disclaimer, _STYLE_DIM))

    doc.build(story)
    return out_path
