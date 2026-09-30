import 'package:flutter/material.dart';
import '../category/category_def.dart';
import '../category/field_spec.dart';
import '../data/nozzles_data.dart';
import '../models/calc_result.dart';
import '../models/catalog_entry.dart';
import '../models/equipment_item.dart';
import '../widgets/app_scope.dart';
import '../widgets/app_shell.dart';
import '../widgets/catalog_picker_sheet.dart';
import '../widgets/category_fields_form.dart';
import '../widgets/common.dart';

class EquipmentFormScreen extends StatefulWidget {
  final String projectId;
  final String kitchenId;
  final String? equipmentId;
  const EquipmentFormScreen({super.key, required this.projectId, required this.kitchenId, this.equipmentId});

  @override
  State<EquipmentFormScreen> createState() => _EquipmentFormScreenState();
}

class _EquipmentFormScreenState extends State<EquipmentFormScreen> {
  late String category;
  late String brand;
  late String model;
  late String notes;
  late Map<String, dynamic> fields;
  late int chosenIdx;
  CatalogRef? catalogRef;
  EquipmentResult? catalogResult;
  late final TextEditingController brandCtrl;
  late final TextEditingController modelCtrl;
  late final TextEditingController notesCtrl;

  @override
  void initState() {
    super.initState();
    final scope = AppScope.read(context);
    final existing = widget.equipmentId != null ? scope.appState.getEquipment(widget.projectId, widget.kitchenId, widget.equipmentId!) : null;
    category = existing?.category ?? 'fryer';
    brand = existing?.brand ?? '';
    model = existing?.model ?? '';
    notes = existing?.notes ?? '';
    fields = Map<String, dynamic>.from(existing?.input ?? {});
    chosenIdx = existing?.chosenIdx ?? 0;
    catalogRef = existing?.catalogRef;
    catalogResult = (catalogRef != null && catalogRef!.hasFixedNozzles) ? existing?.result : null;
    brandCtrl = TextEditingController(text: brand);
    modelCtrl = TextEditingController(text: model);
    notesCtrl = TextEditingController(text: notes);
  }

  @override
  void dispose() {
    brandCtrl.dispose();
    modelCtrl.dispose();
    notesCtrl.dispose();
    super.dispose();
  }

  void _onFieldChanged(String name, dynamic value) {
    setState(() => fields[name] = value);
  }

  Future<void> _openCatalogPicker() async {
    final entry = await showCatalogPickerDialog(context, category: category);
    if (entry == null) return;
    _applyCatalogEntry(entry);
  }

  void _applyCatalogEntry(CatalogEntry entry) {
    final result = _catalogEntryToResult(entry);
    setState(() {
      brand = entry.brand;
      model = entry.model;
      brandCtrl.text = entry.brand;
      modelCtrl.text = entry.model;
      catalogRef = CatalogRef(
        brand: entry.brand,
        model: entry.model,
        notes: entry.notes,
        hmin: entry.hmin,
        hmax: entry.hmax,
        surfaceW: entry.surfaceW,
        surfaceD: entry.surfaceD,
        fuel: entry.fuel,
        hasFixedNozzles: result != null,
        source: entry.source,
      );
      catalogResult = result;
    });
  }

  EquipmentResult? _catalogEntryToResult(CatalogEntry entry) {
    if (entry.nozzles == null || entry.nozzles!.isEmpty) return null;
    final heightRange = (entry.hmin != null && entry.hmax != null)
        ? '${entry.hmin} a ${entry.hmax} in'
        : (entry.hmin != null ? '${entry.hmin} in' : null);
    final flow = entry.nozzles!.fold<num>(0, (s, n) => s + nozzleFlow(n.code) * n.qty);
    final sourceTxt = entry.source == 'user' ? 'Datos de catálogo (agregado por ti)' : 'Datos de catálogo';
    return EquipmentResult(
      nozzles: entry.nozzles!,
      flowNumber: flow,
      heightRange: heightRange,
      detail: '$sourceTxt — ${entry.brand} ${entry.model}.${entry.notes.isNotEmpty ? ' ${entry.notes}' : ''}',
    );
  }

  void _clearCatalog() {
    setState(() {
      catalogRef = null;
      catalogResult = null;
    });
  }

  EquipmentResult? _buildResult() {
    if (catalogResult != null) return catalogResult;
    final def = kCategoryDefs[category]!;
    if (!hasRequiredInputs(def, fields)) return null;
    final outcome = def.compute(fields);
    if (def.hasChoice) {
      if (!outcome.ok || outcome.matches.isEmpty) return null;
      final idx = chosenIdx.clamp(0, outcome.matches.length - 1);
      return def.resultFromChoice?.call(outcome.raw, idx);
    }
    return outcome.ok ? outcome.directResult : null;
  }

  Future<void> _save() async {
    final result = _buildResult();
    if (result == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Complete los datos requeridos antes de guardar.')));
      return;
    }
    final scope = AppScope.read(context);
    if (widget.equipmentId == null) {
      await scope.appState.addEquipment(
        widget.projectId,
        widget.kitchenId,
        EquipmentItem(id: '', category: category, brand: brand, model: model, notes: notes, input: fields, chosenIdx: chosenIdx, catalogRef: catalogRef, result: result, createdAt: 0),
      );
    } else {
      await scope.appState.updateEquipment(widget.projectId, widget.kitchenId, widget.equipmentId!, (old) {
        return old.copyWith(category: category, brand: brand, model: model, notes: notes, input: fields, chosenIdx: chosenIdx, catalogRef: catalogRef, clearCatalogRef: catalogRef == null, result: result);
      });
    }
    if (mounted) scope.navState.back();
  }

  Future<void> _delete() async {
    final ok = await confirmDialog(context, title: 'Eliminar equipo', message: 'Se eliminará este equipo de la cocina.');
    if (!ok) return;
    final scope = AppScope.read(context);
    await scope.appState.deleteEquipment(widget.projectId, widget.kitchenId, widget.equipmentId!);
    if (mounted) scope.navState.back();
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final k = scope.appState.getKitchen(widget.projectId, widget.kitchenId);
    if (k == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => scope.navState.back());
      return const SizedBox.shrink();
    }
    final def = kCategoryDefs[category]!;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => scope.navState.back()),
        title: Text(widget.equipmentId != null ? 'Editar equipo' : 'Nuevo equipo'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1040),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final wide = constraints.maxWidth > 760;
              final fieldsColumn = _buildFieldsColumn(def);
              final resultsColumn = _buildResultsColumn(def);
              if (wide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 3, child: fieldsColumn),
                    const SizedBox(width: 28),
                    Expanded(flex: 2, child: resultsColumn),
                  ],
                );
              }
              return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [fieldsColumn, const SizedBox(height: 20), resultsColumn]);
            },
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 10, 24, 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(onPressed: () => scope.navState.back(), child: const Text('Cancelar')),
                  const SizedBox(width: 10),
                  FilledButton(onPressed: _save, child: const Text('Guardar')),
                ],
              ),
              if (widget.equipmentId != null) ...[
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(foregroundColor: Colors.red.shade700, side: BorderSide(color: Colors.red.shade200)),
                    onPressed: _delete,
                    child: const Text('Eliminar este equipo'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFieldsColumn(CategoryDef def) {
    final refSourceTxt = catalogRef?.source == 'user' ? 'agregado por ti' : 'manual ANSUL R-102';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<String>(
          value: category,
          decoration: const InputDecoration(labelText: 'Tipo de equipo / elemento'),
          items: kCategoryLabels.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
          onChanged: (v) {
            if (v == null) return;
            setState(() {
              category = v;
              fields = {};
              chosenIdx = 0;
            });
          },
        ),
        const SizedBox(height: 18),
        Row(children: [
          Expanded(
            child: TextField(
              controller: brandCtrl,
              decoration: const InputDecoration(labelText: 'Marca', hintText: 'Ej. Frymaster, Vulcan, Ansul...'),
              onChanged: (v) => brand = v,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: modelCtrl,
              decoration: const InputDecoration(labelText: 'Modelo', hintText: 'Ej. MJ-CF, GTI-24...'),
              onChanged: (v) => model = v,
            ),
          ),
        ]),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton(onPressed: _openCatalogPicker, child: const Text('Buscar en catálogo de equipos (marca/modelo)')),
        ),
        const SizedBox(height: 16),
        if (catalogResult != null)
          AppBanner(
            'Usando datos de catálogo ($refSourceTxt): ${catalogRef!.brand} ${catalogRef!.model}. '
            'Las boquillas y la altura de montaje vienen del catálogo, no se calculan a partir de medidas capturadas.',
            kind: BannerKind.ok,
            trailing: OutlinedButton(onPressed: _clearCatalog, child: const Text('Quitar y capturar medidas manualmente')),
          )
        else if (catalogRef != null)
          AppBanner(
            'Referencia de catálogo ($refSourceTxt) — ${catalogRef!.brand} ${catalogRef!.model}: ${catalogRef!.notes.isNotEmpty ? catalogRef!.notes : 'sin combinación de boquillas fija.'} '
            'Capture las medidas abajo para calcular con el método estándar.',
            trailing: OutlinedButton(onPressed: _clearCatalog, child: const Text('Quitar referencia')),
          ),
        if (catalogResult == null) CategoryFieldsForm(key: ValueKey(category), specs: def.fieldSpecs(fields), fields: fields, onFieldChanged: _onFieldChanged),
        const SizedBox(height: 18),
        TextField(
          controller: notesCtrl,
          maxLines: 3,
          decoration: const InputDecoration(labelText: 'Notas (opcional)', hintText: 'Observaciones para el reporte...'),
          onChanged: (v) => notes = v,
        ),
      ],
    );
  }

  Widget _buildResultsColumn(CategoryDef def) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionTitle('Cálculo de boquillas'),
        _buildResultsPanel(def),
      ],
    );
  }

  Widget _buildResultsPanel(CategoryDef def) {
    if (catalogResult != null) {
      final r = catalogResult!;
      final nozzTxt = r.nozzles.map((n) => '${n.code} ×${n.qty}').join(' + ');
      return AppBanner(
        '$nozzTxt · Flow number: ${fmtNum(r.flowNumber)}${r.heightRange != null ? ' · Altura de la boquilla: ${r.heightRange}' : ''}\n${r.detail}',
        kind: BannerKind.ok,
      );
    }
    if (!hasRequiredInputs(def, fields)) {
      return const AppBanner('Complete las medidas del equipo arriba para ver las boquillas disponibles.');
    }
    final outcome = def.compute(fields);
    if (def.hasChoice) {
      if (!outcome.ok || outcome.matches.isEmpty) {
        return AppBanner(def.notFitMsg(fields, outcome.raw), kind: BannerKind.warn);
      }
      if (chosenIdx >= outcome.matches.length) chosenIdx = 0;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ...List.generate(outcome.matches.length, (i) {
            final m = outcome.matches[i];
            final disp = def.describeOption!(m, outcome.raw);
            final selected = i == chosenIdx;
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: InkWell(
                borderRadius: BorderRadius.circular(10),
                onTap: () => setState(() => chosenIdx = i),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: selected ? const Color(0xFFE8F1FB) : Colors.white,
                    border: Border.all(color: selected ? const Color(0xFF0554A3) : Colors.black12, width: selected ? 1.6 : 1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Radio<int>(value: i, groupValue: chosenIdx, onChanged: (v) => setState(() => chosenIdx = v ?? chosenIdx)),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(disp.label, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13.5)),
                            const SizedBox(height: 2),
                            Text(disp.sub, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                          ],
                        ),
                      ),
                      Text('${fmtNum(disp.flow)} flow', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12.5)),
                    ],
                  ),
                ),
              ),
            );
          }),
          const AppBanner('Se seleccionará automáticamente la opción marcada al guardar. Puede elegir otra según la altura disponible bajo la campana.', kind: BannerKind.ok),
        ],
      );
    } else {
      if (!outcome.ok) {
        return AppBanner(def.notFitMsg(fields, outcome.raw), kind: BannerKind.warn);
      }
      final r = outcome.directResult;
      if (r == null || r.nozzles.isEmpty) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AppBanner(r?.detail ?? ''),
            if (outcome.warningBanner != null) AppBanner(outcome.warningBanner!, kind: BannerKind.warn),
          ],
        );
      }
      final nozzTxt = r.nozzles.map((n) => '${n.code} ×${n.qty}').join(' + ');
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppBanner(
            '$nozzTxt · Flow number: ${fmtNum(r.flowNumber)}${r.heightRange != null ? ' · Altura de la boquilla: ${r.heightRange}' : ''}\n${r.detail}',
            kind: BannerKind.ok,
          ),
          if (outcome.warningBanner != null) AppBanner(outcome.warningBanner!, kind: BannerKind.warn),
        ],
      );
    }
  }
}
