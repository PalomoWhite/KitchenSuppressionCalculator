import 'package:flutter/material.dart';
import '../state/nav_state.dart';
import '../widgets/app_scope.dart';
import '../widgets/common.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final projects = scope.appState.projects;
    return Scaffold(
      appBar: AppBar(title: const Text('Ansul Flow Calculator')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionTitle('Proyectos'),
              if (projects.isEmpty)
                const EmptyState('Aún no tienes proyectos.\nCrea tu primer proyecto para empezar.')
              else
                ...projects.map((p) {
                  final kCount = p.kitchens.length;
                  final eCount = p.kitchens.fold<int>(0, (s, k) => s + k.equipment.length);
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: ListItemCard(
                      title: p.name,
                      subtitle: '$kCount cocina${kCount == 1 ? '' : 's'} · $eCount equipo${eCount == 1 ? '' : 's'} · ${fmtDate(p.createdAt)}',
                      onTap: () => scope.navState.push(NavEntry('project', projectId: p.id)),
                    ),
                  );
                }),
              const SizedBox(height: 8),
              Text(
                'Calculadora de apoyo para diseño de sistemas ANSUL® R-102, basada en el manual de diseño. '
                'No sustituye la verificación de un diseñador certificado R-102. Todos los datos se guardan solo en este dispositivo.',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
