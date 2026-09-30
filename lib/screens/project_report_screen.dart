import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show Uint8List, kIsWeb;
import 'package:flutter/material.dart';
import '../models/catalog_entry.dart';
import '../services/pdf_service.dart';
import '../widgets/app_scope.dart';
import '../widgets/common.dart';

class ProjectReportScreen extends StatefulWidget {
  final String projectId;
  const ProjectReportScreen({super.key, required this.projectId});

  @override
  State<ProjectReportScreen> createState() => _ProjectReportScreenState();
}

class _ProjectReportScreenState extends State<ProjectReportScreen> {
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

  String _slug(String s) => s.trim().toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '_');

  Future<void> _downloadPdf() async {
    final scope = AppScope.read(context);
    final p = scope.appState.getProject(widget.projectId);
    if (p == null) return;
    setState(() => _saving = true);
    try {
      await scope.appState.setLastResponsible(responsibleCtrl.text.trim());
      final bytes = Uint8List.fromList(await buildProjectReportPdf(
        project: p,
        appState: scope.appState,
        responsible: responsibleCtrl.text.trim(),
        date: dateCtrl.text.trim(),
      ));
      final path = await FilePicker.platform.saveFile(
        dialogTitle: 'Guardar reporte general del proyecto',
        fileName: 'reporte_general_${_slug(p.name)}.pdf',
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

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final p = scope.appState.getProject(widget.projectId);
    if (p == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => scope.navState.back());
      return const SizedBox.shrink();
    }
    final ps = scope.appState.projectSummary(p);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: const Text('Reporte general'),
        actions: [
          TopBarAction(label: _saving ? 'Generando…' : 'Descargar PDF', onPressed: _saving ? () {} : _downloadPdf),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(child: TextField(controller: responsibleCtrl, decoration: const InputDecoration(labelText: 'Responsable / elaboró'))),
                const SizedBox(width: 10),
                Expanded(child: TextField(controller: dateCtrl, decoration: const InputDecoration(labelText: 'Fecha'))),
              ]),
              const SizedBox(height: 20),
              Text('Reporte general del proyecto — Sistema ANSUL® R-102', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 6),
              Text('Proyecto: ${p.name}  ·  ${p.kitchens.length} cocina(s)', style: const TextStyle(fontWeight: FontWeight.w600)),
              const SectionTitle('Resumen general de materiales (todas las cocinas)'),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('Cocinas: ${p.kitchens.length}'),
                    Text('Tanques totales a instalar: ${ps.totalTanks}'),
                    Text('Galonaje total de agente: ${fmtNum(ps.totalGallons)} gal'),
                  ]),
                ),
              ),
              const AppBanner(
                'Cada cocina cuenta con su propio sistema independiente (tanque(s) propio(s)). Este resumen suma los materiales de todas '
                'las cocinas del proyecto para efectos de compra/logística.',
              ),
              const SectionTitle('Detalle por cocina'),
              ...ps.kitchenSummaries.map((entry) {
                final k = entry.kitchen;
                final s = entry.summary;
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(k.name, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
                        const SizedBox(height: 8),
                        ...k.equipment.map((item) {
                          final r = item.result;
                          final nozzTxt = (r != null && r.nozzles.isNotEmpty) ? r.nozzles.map((n) => '${n.qty}×${n.code}').join(', ') : '—';
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text('${item.displayLabel(kCategoryLabels)} — $nozzTxt · Flow: ${fmtNum(r?.flowNumber)}', style: const TextStyle(fontSize: 12.5)),
                          );
                        }),
                        const SizedBox(height: 8),
                        Text('Flow number total: ${fmtNum(s.totalFlow)} · Tanque(s): ${s.tanks.tankCount} · Galonaje: ${fmtNum(s.tanks.totalGallons)} gal',
                            style: const TextStyle(fontSize: 12.5)),
                      ],
                    ),
                  ),
                );
              }),
              const SizedBox(height: 10),
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
