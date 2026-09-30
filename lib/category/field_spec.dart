/// Especificación declarativa de un campo del formulario de equipo — el
/// equivalente Flutter de las funciones numInput/selectInput/toggleInput de
/// app2.js, pero como datos en vez de HTML.
class SelectOption {
  final String value;
  final String label;
  const SelectOption(this.value, this.label);
}

abstract class FieldSpec {
  final String name;
  final String label;
  const FieldSpec(this.name, this.label);
}

class NumberFieldSpec extends FieldSpec {
  final String? hint;
  const NumberFieldSpec(super.name, super.label, {this.hint});
}

class SelectFieldSpec extends FieldSpec {
  final List<SelectOption> options;
  const SelectFieldSpec(super.name, super.label, this.options);
}

class ToggleFieldSpec extends FieldSpec {
  const ToggleFieldSpec(super.name, super.label);
}

/// Un grupo de campos mostrados uno junto a otro (equivalente a .field-row).
class FieldRowSpec extends FieldSpec {
  final List<FieldSpec> children;
  const FieldRowSpec(this.children) : super('', '');
}

/// Texto informativo (equivalente a .banner-info dentro del formulario).
class InfoBannerSpec extends FieldSpec {
  const InfoBannerSpec(String text) : super('', text);
}

/// Un subtítulo de sección dentro del formulario.
class SectionTitleSpec extends FieldSpec {
  const SectionTitleSpec(String text) : super('', text);
}

num parseNum(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v;
  if (v is bool) return 0;
  return num.tryParse(v.toString()) ?? 0;
}

bool asBool(dynamic v) => v == true || v == 'true';

String asStr(dynamic v, [String fallback = '']) => v == null ? fallback : v.toString();
