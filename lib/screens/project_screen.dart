import 'package:flutter/material.dart';
import '../state/app_state.dart';
import '../state/nav_state.dart';
import '../widgets/app_scope.dart';
import '../widgets/app_shell.dart';
import '../widgets/common.dart';

class ProjectScreen extends StatelessWidget {
  final String projectId;
  const ProjectScreen({super.key, required this.projectId});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final p = scope.appState.getProject(projectId);
    if (p == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => scope.navState.goHome());
      return const SizedBox.shrink();
    }
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: Text(p.name),
        actions: [
          TopBarAction(
            label: 'Renombrar',
            onPressed: () => promptDialog(
              context,
              title: 'Renombrar proyecto',
              label: 'Nombre del proyecto',
              initialValue: p.name,
              onSave: (name) => scope.appState.renameProject(p.id, name),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionTitle('Cocinas'),
              if (p.kitchens.isEmpty)
                const EmptyState('Este proyecto no tiene cocinas todavía.')
              else
                ...p.kitchens.map((k) {
                  final s = scope.appState.kitchenSummary(k);
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: ListItemCard(
                      title: k.name,
                      subtitle: '${k.equipment.length} equipo${k.equipment.length == 1 ? '' : 's'} · Flow number: ${fmtNum(s.totalFlow)} · '
                          '${s.tanks.tankCount} tanque${s.tanks.tankCount == 1 ? '' : 's'}',
                      onTap: () => scope.navState.push(NavEntry('kitchen', projectId: p.id, kitchenId: k.id)),
                    ),
                  );
                }),
              const SizedBox(height: 10),
              FilledButton.icon(
                onPressed: () => _newKitchen(context),
                icon: const Icon(Icons.add),
                label: const Text('Agregar cocina'),
              ),
              if (p.kitchens.isNotEmpty) ...[
                const SizedBox(height: 10),
                OutlinedButton(
                  onPressed: () => scope.navState.push(NavEntry('projectReport', projectId: p.id)),
                  child: const Text('Reporte general del proyecto'),
                ),
              ],
              const SizedBox(height: 24),
              OutlinedButton(
                style: OutlinedButton.styleFrom(foregroundColor: Colors.red.shade700, side: BorderSide(color: Colors.red.shade200)),
                onPressed: () async {
                  final ok = await confirmDialog(context,
                      title: 'Eliminar proyecto', message: 'Se eliminará "${p.name}" y todas sus cocinas y equipos. Esta acción no se puede deshacer.');
                  if (ok) {
                    await scope.appState.deleteProject(p.id);
                    if (context.mounted) scope.navState.goHome();
                  }
                },
                child: const Text('Eliminar proyecto'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _newKitchen(BuildContext context) {
    final scope = AppScope.read(context);
    promptDialog(
      context,
      title: 'Nueva cocina',
      label: 'Nombre de la cocina',
      onSave: (name) async {
        final AppState appState = scope.appState;
        final k = await appState.addKitchen(projectId, name);
        if (k != null) scope.navState.push(NavEntry('kitchen', projectId: projectId, kitchenId: k.id));
      },
    );
  }
}
