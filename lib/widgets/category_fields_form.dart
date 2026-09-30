import 'package:flutter/material.dart';
import '../category/field_spec.dart';
import 'common.dart';

/// Renderiza los campos declarados por CategoryDef.fieldSpecs() para la
/// categoría activa. Mantiene sus propios TextEditingController (uno por
/// nombre de campo, cacheado en el estado de este widget) para que escribir
/// en un campo numérico no pierda el foco/cursor cuando el padre se
/// reconstruye tras cada cambio (equivalente a que app2.js solo reemplace
/// el HTML de los campos que cambian, no todo el formulario).
class CategoryFieldsForm extends StatefulWidget {
  final List<FieldSpec> specs;
  final Map<String, dynamic> fields;
  final void Function(String name, dynamic value) onFieldChanged;

  const CategoryFieldsForm({super.key, required this.specs, required this.fields, required this.onFieldChanged});

  @override
  State<CategoryFieldsForm> createState() => _CategoryFieldsFormState();
}

class _CategoryFieldsFormState extends State<CategoryFieldsForm> {
  final Map<String, TextEditingController> _controllers = {};

  TextEditingController _ctrlFor(String name) {
    return _controllers.putIfAbsent(name, () {
      final initial = widget.fields[name];
      return TextEditingController(text: initial == null ? '' : initial.toString());
    });
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: widget.specs.map((spec) => _buildSpec(spec)).toList(),
    );
  }

  Widget _buildSpec(FieldSpec spec) {
    if (spec is SectionTitleSpec) {
      return SectionTitle(spec.label);
    }
    if (spec is InfoBannerSpec) {
      return AppBanner(spec.label);
    }
    if (spec is FieldRowSpec) {
      // Sin padding extra abajo: cada campo hijo ya trae su propio bottom:18
      // (vía _buildSpec), así el espacio después de la fila queda igual de
      // generoso que después de un campo normal, sin sumarse dos veces.
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: spec.children
            .map((c) => Expanded(child: Padding(padding: const EdgeInsets.only(right: 10), child: _buildSpec(c))))
            .toList(),
      );
    }
    if (spec is NumberFieldSpec) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 18),
        child: TextField(
          controller: _ctrlFor(spec.name),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(
            labelText: spec.label,
            helperText: spec.hint,
            helperMaxLines: 3,
          ),
          onChanged: (v) => widget.onFieldChanged(spec.name, v),
        ),
      );
    }
    if (spec is SelectFieldSpec) {
      final current = widget.fields[spec.name]?.toString();
      final value = spec.options.any((o) => o.value == current) ? current : spec.options.first.value;
      return Padding(
        padding: const EdgeInsets.only(bottom: 18),
        child: DropdownButtonFormField<String>(
          value: value,
          decoration: InputDecoration(labelText: spec.label),
          items: spec.options.map((o) => DropdownMenuItem(value: o.value, child: Text(o.label))).toList(),
          onChanged: (v) {
            if (v != null) widget.onFieldChanged(spec.name, v);
          },
        ),
      );
    }
    if (spec is ToggleFieldSpec) {
      final current = asBool(widget.fields[spec.name]);
      return Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: Text(spec.label, style: const TextStyle(fontSize: 14)),
          value: current,
          onChanged: (v) => widget.onFieldChanged(spec.name, v),
        ),
      );
    }
    return const SizedBox.shrink();
  }
}
