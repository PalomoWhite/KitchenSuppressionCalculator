import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

import '../data/nozzles_data.dart';
import '../models/catalog_entry.dart';
import '../models/kitchen.dart';
import '../models/project.dart';
import '../state/app_state.dart';
import '../widgets/common.dart' show fmtNum;

// Mismo azul de marca que la app, para encabezados dentro del PDF.
final _brand = PdfColor.fromInt(0xFF0554A3);
final _dim = PdfColor.fromInt(0xFF5A6472);

const _disclaimerKitchen =
    'Reporte generado con Ansul Flow Calculator como ayuda de diseño preliminar con base en el manual ANSUL® R-102 (Part No. 418087). '
    'No sustituye la verificación, sello y responsiva de un diseñador certificado ANSUL R-102 conforme a NFPA 17A y los códigos locales '
    'aplicables. Verifique especificaciones específicas por marca/modelo de equipo antes de instalar.';

const _disclaimerProject =
    'Reporte generado con Ansul Flow Calculator como ayuda de diseño preliminar con base en el manual ANSUL® R-102 (Part No. 418087). '
    'No sustituye la verificación, sello y responsiva de un diseñador certificado ANSUL R-102 conforme a NFPA 17A y los códigos locales aplicables.';

pw.Widget _heading(String text, {double size = 14, bool rule = false}) {
  return pw.Container(
    margin: const pw.EdgeInsets.only(top: 14, bottom: 6),
    child: pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(text, style: pw.TextStyle(fontSize: size, fontWeight: pw.FontWeight.bold, color: rule ? _brand : PdfColors.black)),
        if (rule) pw.Container(margin: const pw.EdgeInsets.only(top: 3), height: 0.8, color: _brand),
      ],
    ),
  );
}

pw.Widget _metaBlock({required String responsible, required String date, required List<pw.Widget> lines}) {
  return pw.Container(
    margin: const pw.EdgeInsets.only(bottom: 8),
    child: pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
      ...lines,
      pw.SizedBox(height: 2),
      pw.Text('Responsable: $responsible   ·   Fecha: $date', style: pw.TextStyle(fontSize: 10, color: _dim)),
    ]),
  );
}

pw.Widget _equipmentTable(Kitchen kitchen) {
  final rows = kitchen.equipment.map((item) {
    final r = item.result;
    final nozzTxt = (r != null && r.nozzles.isNotEmpty) ? r.nozzles.map((n) => '${n.code} ×${n.qty}').join(', ') : '-';
    final brandModel = [item.brand, item.model].where((s) => s.trim().isNotEmpty).join(' ');
    return [
      item.displayLabel(kCategoryLabels),
      brandModel.isEmpty ? '-' : brandModel,
      nozzTxt,
      fmtNum(r?.flowNumber),
    ];
  }).toList();
  return pw.TableHelper.fromTextArray(
    headers: const ['Tipo', 'Marca / Modelo', 'Boquillas', 'Flow No.'],
    data: rows,
    headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 9.5, color: PdfColors.white),
    headerDecoration: pw.BoxDecoration(color: _brand),
    cellStyle: const pw.TextStyle(fontSize: 9.5),
    cellAlignments: {3: pw.Alignment.centerRight},
    columnWidths: {0: const pw.FlexColumnWidth(1.9), 1: const pw.FlexColumnWidth(2.1), 2: const pw.FlexColumnWidth(1.6), 3: const pw.FlexColumnWidth(0.9)},
    cellPadding: const pw.EdgeInsets.symmetric(horizontal: 5, vertical: 4),
  );
}

pw.Widget _materialsTable(KitchenSummary s) {
  final rows = <List<String>>[
    ['Flow number total', fmtNum(s.totalFlow)],
    if (s.tanks.tankCount == 0)
      ['Tanques', '-']
    else
      ..._tankCounts(s.tanks.tanks).entries.map((e) => ['Tanque de ${e.key} gal', '${e.value}']),
    ['Galonaje total de agente', '${fmtNum(s.tanks.totalGallons)} gal'],
    ['Cartucho - opción nitrógeno (N2)', s.tanks.n2 ?? '-'],
    ['Cartucho - opción CO2 (alternativa al N2, no ambos)', s.tanks.co2 ?? '-'],
  ];
  return pw.TableHelper.fromTextArray(
    data: rows,
    cellStyle: const pw.TextStyle(fontSize: 9.5),
    cellAlignments: {1: pw.Alignment.centerRight},
    columnWidths: {0: const pw.FlexColumnWidth(2.6), 1: const pw.FlexColumnWidth(1.4)},
    cellPadding: const pw.EdgeInsets.symmetric(horizontal: 5, vertical: 4),
    border: null,
  );
}

Map<num, int> _tankCounts(List<num> tanks) {
  final m = <num, int>{};
  for (final t in tanks) {
    m[t] = (m[t] ?? 0) + 1;
  }
  return m;
}

pw.Widget _nozzleBreakdownTable(Map<String, int> nozzleTotals) {
  final codes = nozzleTotals.keys.toList()..sort();
  final rows = codes.map((c) => [c, nozzlePartNo(c), '${nozzleTotals[c]}']).toList();
  return pw.TableHelper.fromTextArray(
    headers: const ['Boquilla (modelo)', 'No. de parte', 'Cantidad'],
    data: rows.isEmpty ? [['Sin equipos calculados', '', '']] : rows,
    headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 9.5, color: PdfColors.white),
    headerDecoration: pw.BoxDecoration(color: _brand),
    cellStyle: const pw.TextStyle(fontSize: 9.5),
    cellAlignments: {2: pw.Alignment.centerRight},
    cellPadding: const pw.EdgeInsets.symmetric(horizontal: 5, vertical: 4),
  );
}

Future<List<int>> buildKitchenReportPdf({
  required Project project,
  required Kitchen kitchen,
  required AppState appState,
  required String responsible,
  required String date,
}) async {
  final doc = pw.Document();
  final s = appState.kitchenSummary(kitchen);
  doc.addPage(
    pw.MultiPage(
      pageFormat: PdfPageFormat.letter,
      margin: const pw.EdgeInsets.fromLTRB(36, 40, 36, 36),
      build: (context) => [
        _heading('Reporte de cálculo - Sistema ANSUL® R-102', size: 15),
        _metaBlock(responsible: responsible, date: date, lines: [
          pw.Text('Proyecto: ${project.name}   ·   Cocina: ${kitchen.name}', style: const pw.TextStyle(fontSize: 10.5)),
        ]),
        _heading('Equipos, ductos y plenos', rule: true),
        _equipmentTable(kitchen),
        _heading('Resumen de materiales - ${kitchen.name}', rule: true),
        _materialsTable(s),
        _heading('Boquillas requeridas - ${kitchen.name}', rule: true),
        _nozzleBreakdownTable(s.nozzleTotals),
        pw.SizedBox(height: 16),
        pw.Text(_disclaimerKitchen, style: pw.TextStyle(fontSize: 8, color: _dim)),
      ],
    ),
  );
  return doc.save();
}

Future<List<int>> buildProjectReportPdf({
  required Project project,
  required AppState appState,
  required String responsible,
  required String date,
}) async {
  final doc = pw.Document();
  final ps = appState.projectSummary(project);
  doc.addPage(
    pw.MultiPage(
      pageFormat: PdfPageFormat.letter,
      margin: const pw.EdgeInsets.fromLTRB(36, 40, 36, 36),
      build: (context) => [
        _heading('Reporte general del proyecto - Sistema ANSUL® R-102', size: 15),
        _metaBlock(responsible: responsible, date: date, lines: [
          pw.Text('Proyecto: ${project.name}   ·   ${project.kitchens.length} cocina(s)', style: const pw.TextStyle(fontSize: 10.5)),
        ]),
        _heading('Resumen general de materiales (todas las cocinas)', rule: true),
        pw.TableHelper.fromTextArray(
          data: [
            ['Cocinas', '${project.kitchens.length}'],
            ['Tanques totales a instalar', '${ps.totalTanks}'],
            ['Galonaje total de agente', '${fmtNum(ps.totalGallons)} gal'],
          ],
          cellStyle: const pw.TextStyle(fontSize: 9.5),
          cellAlignments: {1: pw.Alignment.centerRight},
          cellPadding: const pw.EdgeInsets.symmetric(horizontal: 5, vertical: 4),
        ),
        pw.SizedBox(height: 6),
        _nozzleBreakdownTable(ps.nozzleTotals),
        pw.SizedBox(height: 6),
        pw.Text(
          'Cada cocina cuenta con su propio sistema independiente (tanque(s) propio(s)). Este resumen suma los materiales de todas las '
          'cocinas del proyecto para efectos de compra/logística.',
          style: pw.TextStyle(fontSize: 8.5, color: _dim),
        ),
        _heading('Detalle por cocina', size: 13, rule: true),
        for (final entry in ps.kitchenSummaries) ...[
          pw.SizedBox(height: 6),
          pw.Text(entry.kitchen.name, style: pw.TextStyle(fontSize: 11.5, fontWeight: pw.FontWeight.bold, color: _brand)),
          pw.SizedBox(height: 4),
          _equipmentTable(entry.kitchen),
          pw.SizedBox(height: 4),
          _materialsTable(entry.summary),
          pw.SizedBox(height: 4),
          _nozzleBreakdownTable(entry.summary.nozzleTotals),
        ],
        pw.SizedBox(height: 16),
        pw.Text(_disclaimerProject, style: pw.TextStyle(fontSize: 8, color: _dim)),
      ],
    ),
  );
  return doc.save();
}
