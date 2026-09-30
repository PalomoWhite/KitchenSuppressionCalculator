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

from . import data as D
from . import engine as E
from .category_defs import category_display_label
from .store import today_iso

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


def _nozzle_breakdown_table(nozzle_totals, total_width):
    codes = sorted(nozzle_totals.keys())
    header = ['Boquilla (modelo)', 'No. de parte', 'Cantidad']
    if not codes:
        rows = [['Sin riesgos calculados', '—', '—']]
    else:
        rows = [[c, D.NOZZLES[c]['partNo'] if c in D.NOZZLES else '—', str(nozzle_totals[c])] for c in codes]
    widths = [total_width * 1.6 / 3.9, total_width * 1.3 / 3.9, total_width * 1.0 / 3.9]
    return _table(rows, widths, header=header, num_cols={2})


def _summary_rows(summary):
    rows = [['Capacidad total de flujo del sistema (flow number)', E.fmt_num(summary['totalFlow'])]]
    tanks = summary['tanks']
    if tanks.get('manual'):
        rows.append(['Selección de tanques', 'Manual (elegida por el usuario)'])
    if tanks.get('tankCount'):
        counts = E.tank_counts(tanks['tanks'])
        for g in sorted(counts.keys(), reverse=True):
            rows.append([f'Tanque de {g} gal', str(counts[g])])
    rows.append(['Galonaje total de agente', f"{E.fmt_num(tanks.get('totalGallons'))} gal"])
    rows.append(['Cartucho — opción nitrógeno (N2)', tanks.get('n2') or '—'])
    rows.append(['Cartucho — opción CO2 (alternativa al N2, no ambos)', tanks.get('co2') or '—'])
    return rows


def _equipment_rows(kitchen):
    rows = []
    for item in kitchen.get('equipment', []):
        r = item.get('result') or {}
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (r.get('nozzles') or [])) or '—'
        brand_model = ' '.join(x for x in [item.get('brand'), item.get('model')] if x) or '—'
        rows.append([category_display_label(item), brand_model, nozz_txt, E.fmt_num(r.get('flowNumber'))])
    return rows


DISCLAIMER = D.PDF_DISCLAIMER


def _header_block(story, title, subtitle, project_name, extra_line, responsible, date, quote_number=''):
    story.append(Paragraph(title, _STYLE_TITLE))
    story.append(Paragraph(subtitle, _STYLE_SUBTITLE))
    story.append(Paragraph(extra_line, _STYLE_PARA))
    resp_line = f"Responsable: {responsible or '—'}&nbsp;&nbsp;&nbsp;&nbsp;Fecha: {date or '—'}"
    if quote_number:
        resp_line += f"&nbsp;&nbsp;&nbsp;&nbsp;No. de cotización: {quote_number}"
    story.append(Paragraph(resp_line, _STYLE_PARA))
    story.append(Spacer(1, 6))


def build_kitchen_report_pdf(project, kitchen, out_path, responsible='', date=None, quote_number=''):
    date = date or today_iso()
    s = E.kitchen_summary(kitchen)
    total_width = letter[0] - 2 * MARGIN

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                             leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    _header_block(story, 'Ansul Flow Calculator — Reporte de cálculo', 'Sistema ANSUL(R) R-102',
                  project['name'], f"Proyecto: {project['name']}&nbsp;&nbsp;&nbsp;&nbsp;Sistema: {kitchen['name']}",
                  responsible, date, quote_number)

    story.append(Paragraph('Riesgos, ductos y plenos', _STYLE_SECTION))
    eq_rows = _equipment_rows(kitchen)
    widths = [total_width * w / 6 for w in (1.9, 2.1, 1.3, 0.7)]
    story.append(_table(eq_rows or [['Sin riesgos', '—', '—', '—']], widths,
                         header=['Tipo', 'Marca / Modelo', 'Boquillas', 'Flow'], num_cols={3}))
    story.append(Spacer(1, 8))

    story.append(Paragraph(f"Resumen de materiales — {kitchen['name']}", _STYLE_SECTION))
    widths2 = [total_width * 3 / 4, total_width * 1 / 4]
    story.append(_table(_summary_rows(s), widths2, header=['Concepto', 'Cantidad'], num_cols={1}))
    if s['tanks'].get('note'):
        story.append(Spacer(1, 4))
        story.append(Paragraph(s['tanks']['note'], _STYLE_NOTE))
    story.append(Spacer(1, 8))

    story.append(Paragraph(f"Boquillas requeridas — {kitchen['name']}", _STYLE_SECTION))
    story.append(_nozzle_breakdown_table(s['nozzleTotals'], total_width))
    story.append(Spacer(1, 14))
    story.append(Paragraph(DISCLAIMER, _STYLE_DIM))

    doc.build(story)
    return out_path


def build_project_report_pdf(project, out_path, responsible='', date=None, quote_number=''):
    date = date or today_iso()
    ps = E.project_summary(project)
    total_width = letter[0] - 2 * MARGIN

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                             leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    _header_block(story, 'Ansul Flow Calculator — Reporte general del proyecto', 'Sistema ANSUL(R) R-102',
                  project['name'], f"Proyecto: {project['name']}&nbsp;&nbsp;&nbsp;&nbsp;Sistemas: {len(project['kitchens'])}",
                  responsible, date, quote_number)

    story.append(Paragraph('Resumen general de materiales (todos los sistemas)', _STYLE_SECTION))
    overall_rows = [
        ['Sistemas', str(len(project['kitchens']))],
        ['Capacidad total de flujo del proyecto (flow number)', E.fmt_num(ps['totalFlow'])],
        ['Tanques totales a instalar', str(ps['totalTanks'])],
        ['Galonaje total de agente', f"{E.fmt_num(ps['totalGallons'])} gal"],
    ]
    widths2 = [total_width * 3 / 4, total_width * 1 / 4]
    story.append(_table(overall_rows, widths2, header=['Concepto', 'Cantidad'], num_cols={1}))
    story.append(Spacer(1, 6))
    story.append(_nozzle_breakdown_table(ps['nozzleTotals'], total_width))
    story.append(Spacer(1, 10))

    story.append(Paragraph('Detalle por sistema', _STYLE_SECTION))
    widths = [total_width * w / 6 for w in (1.9, 2.1, 1.3, 0.7)]
    for entry in ps['kitchenSummaries']:
        kitchen, summary = entry['kitchen'], entry['summary']
        story.append(Paragraph(kitchen['name'], _STYLE_SUBSECTION))
        eq_rows = _equipment_rows(kitchen)
        story.append(_table(eq_rows or [['Sin riesgos', '—', '—', '—']], widths,
                             header=['Tipo', 'Marca / Modelo', 'Boquillas', 'Flow'], num_cols={3}))
        story.append(Spacer(1, 4))
        story.append(_table(_summary_rows(summary), widths2, header=['Concepto', 'Cantidad'], num_cols={1}))
        if summary['tanks'].get('note'):
            story.append(Spacer(1, 3))
            story.append(Paragraph(summary['tanks']['note'], _STYLE_NOTE))
        story.append(Spacer(1, 4))
        story.append(_nozzle_breakdown_table(summary['nozzleTotals'], total_width))
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 8))
    story.append(Paragraph(DISCLAIMER, _STYLE_DIM))

    doc.build(story)
    return out_path
