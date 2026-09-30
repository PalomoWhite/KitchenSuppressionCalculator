import 'package:flutter/material.dart';
import '../models/catalog_entry.dart';
import 'app_scope.dart';
import 'catalog_entry_form_dialog.dart';

/// Buscador de catálogo por marca/modelo — equivalente a renderCatalogModal()
/// en app2.js. Devuelve la entrada elegida (o recién creada) vía Navigator.pop.
Future<CatalogEntry?> showCatalogPickerDialog(BuildContext context, {required String category}) {
  return showDialog<CatalogEntry?>(
    context: context,
    builder: (ctx) => _CatalogPickerDialog(category: category),
  );
}

class _CatalogPickerDialog extends StatefulWidget {
  final String category;
  const _CatalogPickerDialog({required this.category});

  @override
  State<_CatalogPickerDialog> createState() => _CatalogPickerDialogState();
}

class _CatalogPickerDialogState extends State<_CatalogPickerDialog> {
  final _searchCtrl = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final entries = scope.appState.catalogEntriesForCategory(widget.category);
    final q = _query.trim().toLowerCase();
    final filtered = q.isEmpty ? entries : entries.where((e) => ('${e.brand} ${e.model}').toLowerCase().contains(q)).toList();

    return AlertDialog(
      title: Text('Catálogo — ${kCategoryLabels[widget.category] ?? widget.category}'),
      content: SizedBox(
        width: 480,
        height: 480,
        child: Column(
          children: [
            const Text(
              'Combina los modelos documentados en el manual ANSUL R-102 con los que tú has agregado. No es un listado exhaustivo del mercado.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _searchCtrl,
              autofocus: true,
              decoration: const InputDecoration(labelText: 'Buscar marca o modelo', prefixIcon: Icon(Icons.search)),
              onChanged: (v) => setState(() => _query = v),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: entries.isEmpty
                  ? Center(
                      child: Text(
                        'El catálogo aún no incluye modelos específicos para «${kCategoryLabels[widget.category] ?? widget.category}». '
                        'Puede capturar las medidas manualmente al cerrar esta ventana, o agregar un modelo propio abajo.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.black54, fontSize: 12.5),
                      ),
                    )
                  : (filtered.isEmpty
                      ? Center(child: Text('Sin resultados para «$_query».', style: const TextStyle(color: Colors.black54)))
                      : ListView.builder(
                          itemCount: filtered.length,
                          itemBuilder: (ctx, i) {
                            final e = filtered[i];
                            final nozzTxt = (e.nozzles != null && e.nozzles!.isNotEmpty)
                                ? e.nozzles!.map((n) => '${n.code} ×${n.qty}').join(', ')
                                : 'Sin boquillas fijas (referencia)';
                            final heightTxt = (e.hmin != null && e.hmax != null) ? '${e.hmin}-${e.hmax} in' : (e.hmin != null ? '${e.hmin} in' : '');
                            return ListTile(
                              contentPadding: EdgeInsets.zero,
                              title: Text('${e.brand} — ${e.model}', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13.5)),
                              subtitle: Text(
                                '$nozzTxt${heightTxt.isNotEmpty ? ' · Altura: $heightTxt' : ''}\n${e.source == 'user' ? 'Agregado por ti' : 'Manual R-102'}',
                                style: const TextStyle(fontSize: 12),
                              ),
                              isThreeLine: true,
                              onTap: () => Navigator.of(context).pop(e),
                            );
                          },
                        )),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(null), child: const Text('Cerrar')),
        FilledButton(
          onPressed: () async {
            final created = await showCatalogEntryFormDialog(context, defaultCategory: widget.category);
            if (created != null && context.mounted) Navigator.of(context).pop(created);
          },
          child: const Text('+ Agregar modelo nuevo'),
        ),
      ],
    );
  }
}
