import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show Uint8List, kIsWeb;
import 'package:flutter/material.dart';
import '../models/catalog_entry.dart';
import '../services/pdf_service.dart';
import '../widgets/app_scope.dart';
import '../widgets/common.dart';

class KitchenReportScreen extends StatefulWidget {
  final String projectId;
  final String kitchenId;
  const KitchenReportScreen({super.key, required this.projectId, required this.kitchenId});

  @override
  State<KitchenReportScreen> createState() => _KitchenReportScreenState();
}

class _KitchenReportScreenState extends State<KitchenReportScreen> {
  late TextEditingController responsibleCtrl;
  late TextEditingController dateCtrl;
  bool _saving = false;

  String _todayIso() {
    final n = DateTime.now();
    String p2(int v) => v.toString().padLeft(2, '0');
    return '${n.year}-${p2(n.month)}-${p2(n.day)}';
  }

  @override
  void initState() {
    super.initState();
    final scope = AppScope.read(context);
    responsibleCtrl = TextEditingController(text: scope.appState.lastResponsible);
    dateCtrl = TextEditingController(text: _todayIso());
  }

  @override
  void dispose() {
    responsibleCtrl.dispose();
    dateCtrl.dispose();
    super.dispose();
  }

  Future<void> _downloadPdf() async {
    final scope = AppScope.read(context);
    final p = scope.appState.getProject(widget.projectId);
    final k = scope.appState.getKitchen(widget.projectId, widget.kitchenId);
    if (p == null || k == null) return;
    setState(() => _saving = true);
    try {
      await scope.appState.setLastResponsible(responsibleCtrl.text.trim());
      final bytes = Uint8List.fromList(await buildKitchenReportPdf(
        project: p,
        kitchen: k,
        appState: scope.appState,
        responsible: responsibleCtrl.text.trim(),
        date: dateCtrl.text.trim(),
      ));
      final path = await FilePicker.platform.saveFile(
        dialogTitle: 'Guardar reporte de cocina',
        fileName: 'reporte_${_slug(k.name)}.pdf',
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        // En Android/iOS/Web, file_picker escribe el archivo usando estos
        // bytes directamente (no hay acceso de sistema de archivos directo);
        // en Windows/macOS/Linux este parámetro se ignora y el path devuelto
        // se escribe manualmente más abajo.
        bytes: bytes,
      );
      if (path == null) return;
      if (!kIsWeb && (Platform.isWindows || Platform.isMacOS || Platform.isLinux)) {
        await File(path).writeAsBytes(bytes);
      }
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('PDF guardado en $path')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  String _slug(String s) => s.trim().toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '_');

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final p = scope.appState.getProject(widget.projectId);
    final k = scope.appState.getKitchen(widget.projectId, widget.kitchenId);
    if (p == null || k == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => scope.navState.back());
      return const SizedBox.shrink();
    }
    final s = scope.appState.kitchenSummary(k);
    final nozzleCodes = s.nozzleTotals.keys.toList()..sort();

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: const Text('Reporte de cocina'),
        actions: [
          TopBarAction(label: _saving ? 'Generando…' : 'Descargar PDF', onPressed: _saving ? () {} : _downloadPdf),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(child: TextField(controller: responsibleCtrl, decoration: const InputDecoration(labelText: 'Responsable / elaboró'))),
                const SizedBox(width: 10),
                Expanded(child: TextField(controller: dateCtrl, decoration: const InputDecoration(labelText: 'Fecha'))),
              ]),
              const SizedBox(height: 20),
              Text('Reporte de cálculo — Sistema ANSUL® R-102', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 6),
              Text('Proyecto: ${p.name}  ·  Cocina: ${k.name}', style: const TextStyle(fontWeight: FontWeight.w600)),
              const SectionTitle('Equipos, ductos y plenos'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Table(
                    columnWidths: const {0: FlexColumnWidth(1.7), 1: FlexColumnWidth(1.8), 2: FlexColumnWidth(1.4), 3: FlexColumnWidth(0.8)},
                    children: [
                      const TableRow(children: [
                        Padding(padding: EdgeInsets.all(6), child: Text('Tipo', style: TextStyle(fontWeight: FontWeight.w700))),
                        Padding(padding: EdgeInsets.all(6), child: Text('Marca / Modelo', style: TextStyle(fontWeight: FontWeight.w700))),
                        Padding(padding: EdgeInsets.all(6), child: Text('Boquillas', style: TextStyle(fontWeight: FontWeight.w700))),
                        Padding(padding: EdgeInsets.all(6), child: Text('Flow No.', style: TextStyle(fontWeight: FontWeight.w700))),
                      ]),
                      ...k.equipment.map((item) {
                        final r = item.result;
                        final nozzTxt = (r != null && r.nozzles.isNotEmpty) ? r.nozzles.map((n) => '${n.qty}×${n.code}').join(', ') : '—';
                        final brandModel = [item.brand, item.model].where((s) => s.trim().isNotEmpty).join(' ');
                        return TableRow(children: [
                          Padding(padding: const EdgeInsets.all(6), child: Text(item.displayLabel(kCategoryLabels))),
                          Padding(padding: const EdgeInsets.all(6), child: Text(brandModel.isEmpty ? '—' : brandModel)),
                          Padding(padding: const EdgeInsets.all(6), child: Text(nozzTxt)),
                          Padding(padding: const EdgeInsets.all(6), child: Text(fmtNum(r?.flowNumber))),
                        ]);
                      }),
                    ],
                  ),
                ),
              ),
              SectionTitle('Resumen de materiales — ${k.name}'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('Flow number total: ${fmtNum(s.totalFlow)}'),
                    Text('Tanque(s): ${s.tanks.tankCount}'),
                    Text('Galonaje total de agente: ${fmtNum(s.tanks.totalGallons)} gal'),
                    Text('Cartucho — opción nitrógeno (N2): ${s.tanks.n2 ?? '—'}'),
                    Text('Cartucho — opción CO2 (alternativa al N2, no ambos): ${s.tanks.co2 ?? '—'}'),
                    if (s.tanks.note != null) Padding(padding: const EdgeInsets.only(top: 8), child: AppBanner(s.tanks.note!, kind: BannerKind.warn)),
                  ]),
                ),
              ),
              SectionTitle('Boquillas requeridas — ${k.name}'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: nozzleCodes
                        .map((c) => Padding(
                              padding: const EdgeInsets.symmetric(vertical: 3),
                              child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                                Text('Boquilla $c'),
                                Text('${s.nozzleTotals[c]}'),
                              ]),
                            ))
                        .toList(),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Reporte generado con Ansul Flow Calculator como ayuda de diseño preliminar con base en el manual ANSUL® R-102. '
                'No sustituye la verificación, sello y responsiva de un diseñador certificado ANSUL R-102 conforme a NFPA 17A y los '
                'códigos locales aplicables.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
