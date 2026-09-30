import 'package:flutter/material.dart';
import '../models/catalog_entry.dart';
import '../state/nav_state.dart';
import '../widgets/app_scope.dart';
import '../widgets/app_shell.dart';
import '../widgets/common.dart';

class KitchenScreen extends StatelessWidget {
  final String projectId;
  final String kitchenId;
  const KitchenScreen({super.key, required this.projectId, required this.kitchenId});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final k = scope.appState.getKitchen(projectId, kitchenId);
    if (k == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => scope.navState.push(NavEntry('project', projectId: projectId)));
      return const SizedBox.shrink();
    }
    final s = scope.appState.kitchenSummary(k);
    final nozzleCodes = s.nozzleTotals.keys.toList()..sort();

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: Text(k.name),
        actions: [
          TopBarAction(
            label: 'Renombrar',
            onPressed: () => promptDialog(
              context,
              title: 'Renombrar cocina',
              label: 'Nombre de la cocina',
              initialValue: k.name,
              onSave: (name) => scope.appState.renameKitchen(projectId, kitchenId, name),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => scope.navState.push(NavEntry('equipmentForm', projectId: projectId, kitchenId: kitchenId)),
        icon: const Icon(Icons.add),
        label: const Text('Agregar equipo'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 24, 24, 90),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 780),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionTitle('Equipos, ductos y plenos'),
              if (k.equipment.isEmpty)
                const EmptyState('Agrega los equipos, ductos y plenos de esta cocina.')
              else
                ...k.equipment.map((item) {
                  final r = item.result;
                  final nozzTxt = r == null || r.nozzles.isEmpty ? 'Sin boquilla asignada' : r.nozzles.map((n) => '${n.qty}×${n.code}').join(', ');
                  final brandModel = [item.brand, item.model].where((s) => s.trim().isNotEmpty).join(' ');
                  final title = item.displayLabel(kCategoryLabels) + (brandModel.isNotEmpty ? ' — $brandModel' : '');
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: ListItemCard(
                      title: title,
                      subtitle: '$nozzTxt · Flow: ${fmtNum(r?.flowNumber)}',
                      onTap: () => scope.navState.push(NavEntry('equipmentForm', projectId: projectId, kitchenId: kitchenId, equipmentId: item.id)),
                    ),
                  );
                }),
              if (k.equipment.isNotEmpty) ...[
                const SectionTitle('Resumen de la cocina'),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _StatTile(value: fmtNum(s.totalFlow), label: 'Flow number total'),
                    _StatTile(value: '${s.tanks.tankCount}', label: 'Tanque(s) requerido(s)'),
                    _StatTile(value: '${fmtNum(s.tanks.totalGallons)} gal', label: 'Galonaje total de agente'),
                    _StatTile(value: '${s.nozzleTotals.values.fold<int>(0, (a, b) => a + b)}', label: 'Boquillas totales'),
                  ],
                ),
                const SizedBox(height: 14),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                    child: Table(
                      columnWidths: const {0: FlexColumnWidth(2), 1: FlexColumnWidth(1)},
                      children: nozzleCodes
                          .map((c) => TableRow(children: [
                                Padding(padding: const EdgeInsets.all(8), child: Text('Boquilla $c')),
                                Padding(padding: const EdgeInsets.all(8), child: Text('${s.nozzleTotals[c]}', textAlign: TextAlign.right)),
                              ]))
                          .toList(),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                OutlinedButton(
                  onPressed: () => scope.navState.push(NavEntry('kitchenReport', projectId: projectId, kitchenId: kitchenId)),
                  child: const Text('Ver / generar reporte de esta cocina'),
                ),
              ],
              const SizedBox(height: 24),
              OutlinedButton(
                style: OutlinedButton.styleFrom(foregroundColor: Colors.red.shade700, side: BorderSide(color: Colors.red.shade200)),
                onPressed: () async {
                  final ok = await confirmDialog(context, title: 'Eliminar cocina', message: 'Se eliminará "${k.name}" y todos sus equipos.');
                  if (ok) {
                    await scope.appState.deleteKitchen(projectId, kitchenId);
                    if (context.mounted) scope.navState.push(NavEntry('project', projectId: projectId));
                  }
                },
                child: const Text('Eliminar cocina'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  final String value;
  final String label;
  const _StatTile({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 168,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: Colors.black12)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(fontSize: 11.5, color: Colors.grey.shade600)),
        ],
      ),
    );
  }
}
