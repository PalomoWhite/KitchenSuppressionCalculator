import 'package:flutter/material.dart';
import '../data/nozzles_data.dart';
import '../models/calc_result.dart';
import '../models/catalog_entry.dart';
import 'app_scope.dart';
import 'app_shell.dart' show confirmDialog;

/// Formulario de alta/edición de un modelo del catálogo de usuario —
/// equivalente a renderCatalogEntryModalHTML() en app2.js. Se usa tanto
/// desde "Catálogo de equipos" como desde el buscador del formulario de
/// equipo (ahí, al guardar, se aplica de inmediato al equipo abierto).
Future<CatalogEntry?> showCatalogEntryFormDialog(BuildContext context, {CatalogEntry? existing, String? defaultCategory}) {
  return showDialog<CatalogEntry?>(
    context: context,
    builder: (ctx) => _CatalogEntryFormDialog(existing: existing, defaultCategory: defaultCategory),
  );
}

class _NozzleRow {
  String code;
  int qty;
  _NozzleRow(this.code, this.qty);
}

class _CatalogEntryFormDialog extends StatefulWidget {
  final CatalogEntry? existing;
  final String? defaultCategory;
  const _CatalogEntryFormDialog({this.existing, this.defaultCategory});

  @override
  State<_CatalogEntryFormDialog> createState() => _CatalogEntryFormDialogState();
}

class _CatalogEntryFormDialogState extends State<_CatalogEntryFormDialog> {
  late String category = widget.existing?.category ?? widget.defaultCategory ?? 'fryer';
  late final brandCtrl = TextEditingController(text: widget.existing?.brand ?? '');
  late final modelCtrl = TextEditingController(text: widget.existing?.model ?? '');
  String? fuel;
  late final hminCtrl = TextEditingController(text: widget.existing?.hmin?.toString() ?? '');
  late final hmaxCtrl = TextEditingController(text: widget.existing?.hmax?.toString() ?? '');
  late final surfaceWCtrl = TextEditingController(text: widget.existing?.surfaceW?.toString() ?? '');
  late final surfaceDCtrl = TextEditingController(text: widget.existing?.surfaceD?.toString() ?? '');
  late final notesCtrl = TextEditingController(text: widget.existing?.notes ?? '');
  late List<_NozzleRow> nozzleRows = (widget.existing?.nozzles ?? []).map((n) => _NozzleRow(n.code, n.qty)).toList();

  @override
  void initState() {
    super.initState();
    fuel = widget.existing?.fuel;
  }

  @override
  void dispose() {
    brandCtrl.dispose();
    modelCtrl.dispose();
    hminCtrl.dispose();
    hmaxCtrl.dispose();
    surfaceWCtrl.dispose();
    surfaceDCtrl.dispose();
    notesCtrl.dispose();
    super.dispose();
  }

  num? _n(String s) => s.trim().isEmpty ? null : num.tryParse(s.trim());

  Future<void> _save() async {
    final brand = brandCtrl.text.trim();
    final model = modelCtrl.text.trim();
    if (brand.isEmpty || model.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Indique marca y modelo antes de guardar.')));
      return;
    }
    final scope = AppScope.read(context);
    final draft = CatalogEntry(
      category: category,
      brand: brand,
      model: model,
      fuel: fuel,
      nozzles: nozzleRows.isEmpty ? null : nozzleRows.map((r) => NozzleQty(code: r.code, qty: r.qty)).toList(),
      hmin: _n(hminCtrl.text),
      hmax: _n(hmaxCtrl.text),
      surfaceW: _n(surfaceWCtrl.text),
      surfaceD: _n(surfaceDCtrl.text),
      notes: notesCtrl.text.trim(),
      source: 'user',
    );
    CatalogEntry saved;
    if (widget.existing?.id != null) {
      saved = (await scope.appState.updateCatalogEntry(widget.existing!.id!, (_) => draft.copyWith(id: widget.existing!.id, source: 'user'))) ?? draft;
    } else {
      saved = await scope.appState.addCatalogEntry(draft);
    }
    if (mounted) Navigator.of(context).pop(saved);
  }

  Future<void> _delete() async {
    final ok = await confirmDialog(context,
        title: 'Eliminar modelo del catálogo', message: 'Se eliminará este modelo agregado por ti. Los equipos que ya lo usaron conservan sus datos guardados.');
    if (!ok) return;
    final scope = AppScope.read(context);
    await scope.appState.deleteCatalogEntry(widget.existing!.id!);
    if (mounted) Navigator.of(context).pop(null);
  }

  @override
  Widget build(BuildContext context) {
    final nozzleCodes = kNozzles.keys.toList()..sort();
    return AlertDialog(
      title: Text(widget.existing != null ? 'Editar modelo del catálogo' : 'Agregar modelo al catálogo'),
      content: SizedBox(
        width: 480,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Captura los datos de la ficha técnica del fabricante. Queda marcado como «Agregado por ti».',
                  style: TextStyle(fontSize: 12.5, color: Colors.black54)),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: category,
                decoration: const InputDecoration(labelText: 'Tipo de equipo'),
                items: kCatalogCategories.map((c) => DropdownMenuItem(value: c, child: Text(kCategoryLabels[c] ?? c))).toList(),
                onChanged: (v) => setState(() => category = v ?? category),
              ),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(child: TextField(controller: brandCtrl, decoration: const InputDecoration(labelText: 'Marca'))),
                const SizedBox(width: 10),
                Expanded(child: TextField(controller: modelCtrl, decoration: const InputDecoration(labelText: 'Modelo'))),
              ]),
              const SizedBox(height: 12),
              DropdownButtonFormField<String?>(
                value: fuel,
                decoration: const InputDecoration(labelText: 'Combustible (opcional)'),
                items: const [
                  DropdownMenuItem(value: null, child: Text('— No especificado —')),
                  DropdownMenuItem(value: 'gas', child: Text('Gas')),
                  DropdownMenuItem(value: 'electric', child: Text('Eléctrico')),
                  DropdownMenuItem(value: 'charcoal', child: Text('Carbón')),
                  DropdownMenuItem(value: 'wood', child: Text('Leña')),
                ],
                onChanged: (v) => setState(() => fuel = v),
              ),
              const SizedBox(height: 16),
              const Text('Boquillas (según la ficha técnica)', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12.5)),
              const SizedBox(height: 6),
              if (nozzleRows.isEmpty)
                const Padding(
                  padding: EdgeInsets.only(bottom: 8),
                  child: Text('Sin boquillas agregadas — este modelo quedará solo como referencia.', style: TextStyle(fontSize: 12, color: Colors.black54)),
                ),
              ...nozzleRows.asMap().entries.map((entry) {
                final i = entry.key;
                final row = entry.value;
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(
                        flex: 2,
                        child: DropdownButtonFormField<String>(
                          value: row.code,
                          decoration: const InputDecoration(labelText: 'Boquilla'),
                          items: nozzleCodes.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                          onChanged: (v) => setState(() => row.code = v ?? row.code),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextFormField(
                          initialValue: row.qty.toString(),
                          decoration: const InputDecoration(labelText: 'Cant.'),
                          keyboardType: TextInputType.number,
                          onChanged: (v) => row.qty = int.tryParse(v) ?? 1,
                        ),
                      ),
                      IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => setState(() => nozzleRows.removeAt(i))),
                    ],
                  ),
                );
              }),
              OutlinedButton(
                onPressed: () => setState(() => nozzleRows.add(_NozzleRow(nozzleCodes.first, 1))),
                child: const Text('+ Agregar boquilla'),
              ),
              const SizedBox(height: 14),
              Row(children: [
                Expanded(child: TextField(controller: hminCtrl, decoration: const InputDecoration(labelText: 'Altura mín. (in)'), keyboardType: TextInputType.number)),
                const SizedBox(width: 10),
                Expanded(child: TextField(controller: hmaxCtrl, decoration: const InputDecoration(labelText: 'Altura máx. (in)'), keyboardType: TextInputType.number)),
              ]),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(child: TextField(controller: surfaceWCtrl, decoration: const InputDecoration(labelText: 'Ancho de superficie (in, opc.)'), keyboardType: TextInputType.number)),
                const SizedBox(width: 10),
                Expanded(child: TextField(controller: surfaceDCtrl, decoration: const InputDecoration(labelText: 'Fondo de superficie (in, opc.)'), keyboardType: TextInputType.number)),
              ]),
              const SizedBox(height: 12),
              TextField(controller: notesCtrl, maxLines: 3, decoration: const InputDecoration(labelText: 'Notas (opcional)')),
              if (widget.existing != null) ...[
                const SizedBox(height: 16),
                OutlinedButton(
                  style: OutlinedButton.styleFrom(foregroundColor: Colors.red.shade700, side: BorderSide(color: Colors.red.shade200)),
                  onPressed: _delete,
                  child: const Text('Eliminar este modelo'),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(null), child: const Text('Cancelar')),
        FilledButton(onPressed: _save, child: const Text('Guardar')),
      ],
    );
  }
}
