// =========================================================================
// Definición de campos y cálculo por categoría de equipo — puerto directo
// de CATEGORY_DEF en app2.js. Cada entrada sabe: qué campos mostrar en el
// formulario, qué campos son obligatorios antes de calcular, cómo calcular,
// y (si aplica) cómo describir/resolver una opción elegida por el usuario.
// =========================================================================
import '../calc/calc_engine.dart';
import '../data/nozzles_data.dart';
import '../data/grill_data.dart';
import '../data/long_side_area_data.dart';
import '../data/broiler_data.dart';
import '../data/duct_plenum_data.dart';
import '../models/calc_result.dart';
import 'field_spec.dart';

class OptionDisplay {
  final String label;
  final String sub;
  final num flow;
  const OptionDisplay({required this.label, required this.sub, required this.flow});
}

/// Resultado uniforme de compute() para cualquier categoría. `raw` conserva
/// el objeto tipado devuelto por el motor de cálculo (FryerCalcResult,
/// GrillCalcResult, etc.) para que resultFromChoice/notFitMsg lo puedan
/// volver a castear — igual que en JS, donde esas funciones reciben el
/// objeto `c` completo, no solo la lista de matches.
class CategoryCalcOutcome {
  final bool ok;
  final List<dynamic> matches;
  final dynamic raw;
  final EquipmentResult? directResult;
  final String? warningBanner;
  const CategoryCalcOutcome({required this.ok, this.matches = const [], this.raw, this.directResult, this.warningBanner});
}

class CategoryDef {
  final bool hasChoice;
  final List<String> Function(Map<String, dynamic> f) requiredFields;
  final List<FieldSpec> Function(Map<String, dynamic> f) fieldSpecs;
  final CategoryCalcOutcome Function(Map<String, dynamic> f) compute;
  final OptionDisplay Function(dynamic match, dynamic raw)? describeOption;
  final EquipmentResult? Function(dynamic raw, int chosenIdx)? resultFromChoice;
  final String Function(Map<String, dynamic> f, dynamic raw) notFitMsg;
  const CategoryDef({
    required this.hasChoice,
    required this.requiredFields,
    required this.fieldSpecs,
    required this.compute,
    this.describeOption,
    this.resultFromChoice,
    required this.notFitMsg,
  });
}

const _fuelOptsGasElectric = [SelectOption('gas', 'Gas'), SelectOption('electric', 'Eléctrico')];

/// ¿Ya se capturaron los campos obligatorios (con valor numérico > 0) para
/// poder calcular/mostrar boquillas? Puerto de hasRequiredInputs() en app2.js.
bool hasRequiredInputs(CategoryDef def, Map<String, dynamic> f) {
  final req = def.requiredFields(f);
  for (final name in req) {
    final v = f[name];
    if (v == null || v == '') return false;
    final n = num.tryParse(v.toString());
    if (n == null || n <= 0) return false;
  }
  return true;
}

final Map<String, CategoryDef> kCategoryDefs = {
  'fryer': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => asBool(f['hasDripboard']) ? ['frypotD', 'frypotL', 'overallD', 'overallL'] : ['frypotD', 'frypotL'],
    fieldSpecs: (f) => [
      const SelectFieldSpec('fuel', 'Combustible', _fuelOptsGasElectric),
      const ToggleFieldSpec('hasDripboard', '¿Tiene escurridor (dripboard)?'),
      const SectionTitleSpec('Tina (frypot) — sin escurridor'),
      FieldRowSpec([
        const NumberFieldSpec('frypotD', 'Profundidad de la tina (in)', hint: 'De frente a fondo'),
        const NumberFieldSpec('frypotL', 'Ancho de la tina (in)', hint: 'De lado a lado'),
      ]),
      if (asBool(f['hasDripboard'])) ...[
        const SectionTitleSpec('Área total — con escurridor'),
        FieldRowSpec([
          const NumberFieldSpec('overallD', 'Profundidad total (in)', hint: 'De frente a fondo, incluyendo el escurridor'),
          const NumberFieldSpec('overallL', 'Ancho total (in)', hint: 'De lado a lado, incluyendo el escurridor'),
        ]),
      ],
      const NumberFieldSpec('modules', 'Número de módulos / boquillas',
          hint: 'Si la freidora es más grande que la cobertura de una sola boquilla, indique cuántos módulos (secciones) tendrá; capture las dimensiones de UN módulo arriba. Máx. 864 in² de área total.'),
    ],
    compute: (f) {
      final c = calcFryer(
        hasDripboard: asBool(f['hasDripboard']),
        frypotD: parseNum(f['frypotD']),
        frypotL: parseNum(f['frypotL']),
        overallD: parseNum(f['overallD']),
        overallL: parseNum(f['overallL']),
        modules: f['modules'] ?? 1,
        fuel: asStr(f['fuel'], 'gas'),
      );
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as FryerMatch;
      final c = raw as FryerCalcResult;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la tina: ${match.hmin} a ${match.hmax} in · Flow number: ${match.flowPerNozzle}',
        flow: match.flowPerNozzle * c.modules,
      );
    },
    resultFromChoice: (raw, idx) => fryerResultForChoice(raw as FryerCalcResult, idx),
    notFitMsg: (f, raw) {
      final c = raw as FryerCalcResult;
      if (c.overLimit) {
        return 'El área total (${_fmt(c.totalArea)} in²) excede el máximo modularizable de 864 in². Reduzca el tamaño por módulo, aumente el número de módulos, o divídalo en equipos independientes.';
      }
      return 'Ninguna boquilla estándar cubre estas dimensiones exactas. Revise las medidas o consulte a ANSUL para una aplicación específica por marca/modelo.';
    },
  ),

  'tiltskillet': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('modules', 'Número de módulos', hint: 'Use más de un módulo si el sartén excede la cobertura de una sola boquilla.'),
    ],
    compute: (f) {
      final c = calcTiltSkillet(parseNum(f['d1']), parseNum(f['d2']), f['modules'] ?? 1);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as FryerMatch;
      final c = raw as FryerCalcResult;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Flow number: ${match.flowPerNozzle}',
        flow: match.flowPerNozzle * c.modules,
      );
    },
    resultFromChoice: (raw, idx) => tiltSkilletResultForChoice(raw as FryerCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna boquilla estándar cubre estas dimensiones. Revise las medidas o consulte a ANSUL.',
  ),

  'range': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      const SelectFieldSpec('burners', 'Número de quemadores', [SelectOption('2', '2 quemadores'), SelectOption('4', '4 quemadores'), SelectOption('6', '6 quemadores')]),
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho del área de cocción (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo del área de cocción (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('modules', 'Número de módulos', hint: 'Use más de un módulo si el rango excede la cobertura de una sola zona de boquilla(s).'),
    ],
    compute: (f) {
      final c = calcLongSideArea(kRangeOptions, parseNum(f['d1']), parseNum(f['d2']), f['modules'] ?? 1);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as LongSideMatch;
      final c = raw as LongSideCalcResult;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle}${match.qty > 1 ? ' ×${match.qty}' : ''} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Área máx ${match.area} in² · Lado máx ${match.longSide} in',
        flow: match.qty * nozzleFlow(match.nozzle) * c.modules,
      );
    },
    resultFromChoice: (raw, idx) => longSideAreaResultForChoice(raw as LongSideCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna opción estándar cubre esta área. Considere dividir el rango en más módulos.',
  ),

  'griddle': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho de la superficie (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo de la superficie (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('modules', 'Número de módulos', hint: 'Use más de un módulo si la plancha excede la cobertura de una sola boquilla.'),
    ],
    compute: (f) {
      final c = calcLongSideArea(kGriddleOptions, parseNum(f['d1']), parseNum(f['d2']), f['modules'] ?? 1);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as LongSideMatch;
      final c = raw as LongSideCalcResult;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Área máx ${match.area} in² · Lado máx ${match.longSide} in',
        flow: match.qty * nozzleFlow(match.nozzle) * c.modules,
      );
    },
    resultFromChoice: (raw, idx) => longSideAreaResultForChoice(raw as LongSideCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna opción estándar cubre esta área. Considere dividir la plancha en más módulos.',
  ),

  'grill': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      const SelectFieldSpec('fuel', 'Combustible', _fuelOptsGasElectric),
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho de la parrilla (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo de la parrilla (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('depth', 'Profundidad de la cama de lava/cerámica (in, opcional)', hint: 'Solo aplica a variantes con lava rock/cerámica'),
    ],
    compute: (f) {
      final depth = (f['depth'] == null || f['depth'] == '') ? null : parseNum(f['depth']);
      final c = calcGrill(asStr(f['fuel'], 'gas'), parseNum(f['d1']), parseNum(f['d2']), depth);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as GrillMatch;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Área máx ${match.area} in² · Lado máx ${match.longSide} in${match.maxDepth != null ? ' · Profundidad máx ${match.maxDepth} in' : ''}',
        flow: match.qty * nozzleFlow(match.nozzle),
      );
    },
    resultFromChoice: (raw, idx) => grillResultForChoice(raw as GrillCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna variante estándar de parrilla cubre estas dimensiones/combustible. Revise las medidas o consulte a ANSUL.',
  ),

  'naturalcharcoal': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      InfoBannerSpec('Combustible: ${kFuelLabels['charcoal']}'),
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho del asador (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo del asador (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('depth', 'Profundidad del carbón (in, opcional)'),
    ],
    compute: (f) {
      final depth = (f['depth'] == null || f['depth'] == '') ? null : parseNum(f['depth']);
      final c = calcGrill('charcoal', parseNum(f['d1']), parseNum(f['d2']), depth);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as GrillMatch;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Área máx ${match.area} in² · Lado máx ${match.longSide} in${match.maxDepth != null ? ' · Profundidad máx ${match.maxDepth} in' : ''}',
        flow: match.qty * nozzleFlow(match.nozzle),
      );
    },
    resultFromChoice: (raw, idx) => grillResultForChoice(raw as GrillCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna variante estándar de asador de carbón cubre estas dimensiones. Revise las medidas o consulte a ANSUL.',
  ),

  'woodgrill': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['d1', 'd2'],
    fieldSpecs: (f) => [
      InfoBannerSpec('Combustible: ${kFuelLabels['wood']}'),
      FieldRowSpec([
        const NumberFieldSpec('d1', 'Ancho del asador (in)', hint: 'De lado a lado'),
        const NumberFieldSpec('d2', 'Fondo del asador (in)', hint: 'De frente a fondo'),
      ]),
      const NumberFieldSpec('depth', 'Profundidad de la leña (in, opcional)'),
    ],
    compute: (f) {
      final depth = (f['depth'] == null || f['depth'] == '') ? null : parseNum(f['depth']);
      final c = calcGrill('wood', parseNum(f['d1']), parseNum(f['d2']), depth);
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as GrillMatch;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle} — ${match.tag}',
        sub: 'Altura de la boquilla sobre la superficie: ${match.hmin} a ${match.hmax} in · Área máx ${match.area} in² · Lado máx ${match.longSide} in${match.maxDepth != null ? ' · Profundidad máx ${match.maxDepth} in' : ''}',
        flow: match.qty * nozzleFlow(match.nozzle),
      );
    },
    resultFromChoice: (raw, idx) => grillResultForChoice(raw as GrillCalcResult, idx),
    notFitMsg: (f, raw) => 'Ninguna variante estándar de asador de leña cubre estas dimensiones. Revise las medidas o consulte a ANSUL.',
  ),

  'combioven': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => const [],
    fieldSpecs: (f) => [
      const InfoBannerSpec(
          'El manual R-102 no incluye una boquilla estándar para hornos combi con gabinete cerrado (protección tipo UL 300 dentro del gabinete). Este renglón se registra solo como referencia — no aporta boquillas ni flow number. Si el gabinete permanece abierto durante la cocción, consulte a ANSUL para una aplicación específica.'),
    ],
    compute: (f) => const CategoryCalcOutcome(
      ok: true,
      directResult: EquipmentResult(nozzles: [], flowNumber: 0, heightRange: '—', detail: 'Horno Combi — no cubierto por el catálogo estándar R-102 (informativo).'),
    ),
    notFitMsg: (f, raw) => '',
  ),

  'marmita': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => const [],
    fieldSpecs: (f) => [
      const InfoBannerSpec(
          'Las marmitas de vapor/agua (para caldos, salsas, etc.) no manejan aceite ni producen vapores grasos, por lo que normalmente no requieren protección contra incendios conforme al manual ANSUL R-102. Este renglón se registra solo como referencia — no aporta boquillas ni flow number. Si su marmita se usa para freír o de cualquier forma maneja aceite/grasa, no la registre en esta categoría — consulte a ANSUL para la aplicación que corresponda.'),
    ],
    compute: (f) => const CategoryCalcOutcome(
      ok: true,
      directResult: EquipmentResult(nozzles: [], flowNumber: 0, heightRange: '—', detail: 'Marmita — no requiere protección (informativo).'),
    ),
    notFitMsg: (f, raw) => '',
  ),

  'chainbroiler': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => ['length', 'width'],
    fieldSpecs: (f) {
      final kind = asStr(f['kind'], 'horizontal');
      return [
        SelectFieldSpec('kind', 'Tipo de protección', [
          SelectOption('horizontal', kChainBroilerOptions['horizontal']!.label),
          SelectOption('overhead', kChainBroilerOptions['overhead']!.label),
        ]),
        FieldRowSpec([
          const NumberFieldSpec('length', 'Longitud interna (in)', hint: 'De frente a fondo, dentro de la cámara'),
          const NumberFieldSpec('width', 'Ancho interno (in)', hint: 'De lado a lado, dentro de la cámara'),
        ]),
        if (kind == 'overhead') ...[
          FieldRowSpec([
            const NumberFieldSpec('openingL', 'Abertura — largo (in)'),
            const NumberFieldSpec('openingW', 'Abertura — ancho (in)'),
          ]),
          const InfoBannerSpec('Opcional: valida la regla del 60% mínimo de abertura.'),
        ],
      ];
    },
    compute: (f) {
      final kind = asStr(f['kind'], 'horizontal');
      final openingL = (f['openingL'] == null || f['openingL'] == '') ? null : parseNum(f['openingL']);
      final openingW = (f['openingW'] == null || f['openingW'] == '') ? null : parseNum(f['openingW']);
      final c = calcChainBroiler(kind, parseNum(f['length']), parseNum(f['width']), openingL, openingW);
      return CategoryCalcOutcome(ok: c.ok, raw: c, directResult: c.result, warningBanner: c.ratioWarning);
    },
    notFitMsg: (f, raw) {
      final c = raw as ChainBroilerCalcResult;
      return 'Excede el tamaño máximo interno (${c.opt.maxLength} × ${c.opt.maxWidth} in) para esta variante. Pruebe la otra variante o proteja como equipos separados.';
    },
  ),

  'uprightbroiler': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => ['length', 'width'],
    fieldSpecs: (f) => [
      FieldRowSpec([
        const NumberFieldSpec('length', 'Longitud interna (in)', hint: 'De frente a fondo, dentro de la cámara'),
        const NumberFieldSpec('width', 'Ancho interno (in)', hint: 'De lado a lado, dentro de la cámara'),
      ]),
    ],
    compute: (f) {
      final c = calcUprightBroiler(parseNum(f['length']), parseNum(f['width']));
      return CategoryCalcOutcome(ok: c.ok, raw: c, directResult: c.result);
    },
    notFitMsg: (f, raw) => 'Excede el máximo estándar (${kUprightBroiler.maxLength} × ${kUprightBroiler.maxWidth} in). Consulte a ANSUL para aplicación específica.',
  ),

  'salamander': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['length', 'width'],
    fieldSpecs: (f) => [
      FieldRowSpec([
        const NumberFieldSpec('length', 'Longitud interna (in)', hint: 'De frente a fondo'),
        const NumberFieldSpec('width', 'Ancho interno (in)', hint: 'De lado a lado'),
      ]),
    ],
    compute: (f) {
      final c = calcSalamander(parseNum(f['length']), parseNum(f['width']));
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as SalamanderOption;
      return OptionDisplay(label: match.label, sub: 'Superficie máx. protegida: ${match.maxLength} × ${match.maxWidth} in', flow: match.qty * nozzleFlow(match.nozzle));
    },
    resultFromChoice: (raw, idx) {
      final c = raw as SalamanderCalcResult;
      if (idx < 0 || idx >= c.matches.length) return null;
      return salamanderResult(c.matches[idx]);
    },
    notFitMsg: (f, raw) => 'Ninguna de las 3 opciones de salamandra cubre estas dimensiones.',
  ),

  'wok': CategoryDef(
    hasChoice: true,
    requiredFields: (f) => ['diam', 'depth'],
    fieldSpecs: (f) => [
      FieldRowSpec([
        const NumberFieldSpec('diam', 'Diámetro del wok (in)', hint: 'Diámetro superior, boca del wok'),
        const NumberFieldSpec('depth', 'Profundidad del wok (in)', hint: 'Del borde superior al fondo'),
      ]),
    ],
    compute: (f) {
      final c = calcWok(parseNum(f['diam']), parseNum(f['depth']));
      return CategoryCalcOutcome(ok: c.ok, matches: c.matches, raw: c);
    },
    describeOption: (m, raw) {
      final match = m as WokMatch;
      return OptionDisplay(
        label: 'Boquilla ${match.nozzle}',
        sub: 'Diámetro ${match.diamMin}-${match.diamMax} in · Profundidad ${match.depthMin}-${match.depthMax} in · Altura de la boquilla sobre el wok: ${match.hmin}-${match.hmax} in',
        flow: match.qty * nozzleFlow(match.nozzle),
      );
    },
    resultFromChoice: (raw, idx) {
      final c = raw as WokCalcResult;
      if (idx < 0 || idx >= c.matches.length) return null;
      return wokResult(c.matches[idx]);
    },
    notFitMsg: (f, raw) => 'Ningún wok estándar cubre este diámetro/profundidad.',
  ),

  'duct': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => asBool(f['round']) ? ['diameter'] : ['sideA', 'sideB'],
    fieldSpecs: (f) {
      final round = asBool(f['round']);
      return [
        const ToggleFieldSpec('round', 'Ducto redondo'),
        if (round)
          const NumberFieldSpec('diameter', 'Diámetro (in)')
        else
          FieldRowSpec([
            const NumberFieldSpec('sideA', 'Ancho del ducto (in)'),
            const NumberFieldSpec('sideB', 'Alto del ducto (in)'),
          ]),
        const NumberFieldSpec('qty', 'Cantidad de ductos idénticos',
            hint: 'Las boquillas se multiplican por esta cantidad si hay más de un ducto igual en la cocina.'),
      ];
    },
    compute: (f) {
      final round = asBool(f['round']);
      final perimeter = round ? null : 2 * (parseNum(f['sideA']) + parseNum(f['sideB']));
      final diameter = round ? parseNum(f['diameter']) : null;
      final c = calcDuct(perimeter, diameter, round, f['qty'] ?? 1);
      return CategoryCalcOutcome(ok: c.ok, raw: c, directResult: c.result, warningBanner: c.estimated ? c.result?.detail : null);
    },
    notFitMsg: (f, raw) => (raw as DuctCalcResult).msg ?? 'No se pudo calcular con estas medidas.',
  ),

  'plenum': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => ['lengthFt'],
    fieldSpecs: (f) {
      return [
        SelectFieldSpec('kind', 'Tipo de protección', kPlenumOptions.entries.map((e) => SelectOption(e.key, e.value.label)).toList()),
        const NumberFieldSpec('lengthFt', 'Longitud del pleno (ft)'),
        const NumberFieldSpec('qty', 'Cantidad de plenos idénticos',
            hint: 'Las boquillas se multiplican por esta cantidad si hay más de un pleno igual en la cocina.'),
      ];
    },
    compute: (f) {
      final kind = asStr(f['kind'], 'horizSingle1N');
      final lengthFt = parseNum(f['lengthFt']);
      if (lengthFt <= 0) return const CategoryCalcOutcome(ok: false);
      final result = calcPlenum(kind, lengthFt, f['qty'] ?? 1);
      return CategoryCalcOutcome(ok: true, directResult: result);
    },
    notFitMsg: (f, raw) => 'Indique la longitud del pleno.',
  ),

  'precipitator': CategoryDef(
    hasChoice: false,
    requiredFields: (f) => const [],
    fieldSpecs: (f) => [
      const NumberFieldSpec('cells', 'Número de celdas'),
    ],
    compute: (f) => CategoryCalcOutcome(ok: true, directResult: calcPrecipitator(f['cells'] ?? 1)),
    notFitMsg: (f, raw) => '',
  ),
};

String _fmt(num n) {
  final r = (n * 100).round() / 100;
  if (r == r.roundToDouble()) return r.toInt().toString();
  return r.toString();
}
