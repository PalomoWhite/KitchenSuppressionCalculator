import 'package:flutter/material.dart';
import '../models/catalog_entry.dart';
import '../widgets/app_scope.dart';
import '../widgets/catalog_entry_form_dialog.dart';
import '../widgets/common.dart';

/// Catálogo de equipos agregados por el usuario — equivalente a
/// renderCatalogManageView() en app.js.
class CatalogManageScreen extends StatelessWidget {
  const CatalogManageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final custom = List<CatalogEntry>.from(scope.appState.data.customCatalog)
      ..sort((a, b) => ('${a.brand}${a.model}').compareTo('${b.brand}${b.model}'));

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: const Text('Catálogo de equipos'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const AppBanner(
                'Aquí se guardan los modelos que agregas con tus propias fichas técnicas — se distinguen de los modelos tomados del manual '
                'ANSUL R-102 (esos no se pueden editar) y viajan con tus respaldos.',
              ),
              SectionTitle('Tus modelos (${custom.length})'),
              if (custom.isEmpty)
                const EmptyState('Aún no has agregado modelos propios al catálogo.\nAgrega uno cuando tengas la ficha técnica de un equipo que no esté en el catálogo del manual.')
              else
                ...custom.map((e) {
                  final nozzTxt = (e.nozzles != null && e.nozzles!.isNotEmpty)
                      ? e.nozzles!.map((n) => '${n.code} ×${n.qty}').join(', ')
                      : 'Sin boquillas fijas (referencia)';
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: ListItemCard(
                      title: '${e.brand} — ${e.model}',
                      subtitle: '${kCategoryLabels[e.category] ?? e.category} · $nozzTxt',
                      onTap: () => showCatalogEntryFormDialog(context, existing: e),
                    ),
                  );
                }),
              const SizedBox(height: 10),
              FilledButton.icon(
                onPressed: () => showCatalogEntryFormDialog(context),
                icon: const Icon(Icons.add),
                label: const Text('Agregar modelo'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
