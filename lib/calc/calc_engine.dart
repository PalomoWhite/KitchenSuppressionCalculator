// =========================================================================
// Motor de cálculo — puerto directo de calc.js. Traduce entradas del
// usuario en boquillas/flow number usando las tablas de lib/data/*.
// =========================================================================
import 'dart:math' as math;
import '../data/nozzles_data.dart';
import '../data/fryer_data.dart';
import '../data/long_side_area_data.dart';
import '../data/grill_data.dart';
import '../data/wok_data.dart';
import '../data/broiler_data.dart';
import '../data/duct_plenum_data.dart';
import '../models/calc_result.dart';

bool fitsBox(num d1, num d2, num maxA, num maxB) {
  return (d1 <= maxA && d2 <= maxB) || (d1 <= maxB && d2 <= maxA);
}

bool fitsLongSideArea(num d1, num d2, num longSideMax, num areaMax) {
  final longSide = math.max(d1, d2);
  final area = d1 * d2;
  return longSide <= longSideMax + 1e-9 && area <= areaMax + 1e-9;
}

int intOrDefault(dynamic v, int fallback) {
  if (v == null) return fallback;
  if (v is int) return v;
  if (v is num) return v.toInt();
  return int.tryParse(v.toString()) ?? fallback;
}

// ---------- Freidoras / Sartén de volteo ----------------------------------
class FryerMatch {
  final String group;
  final String nozzle;
  final String tag;
  final num hmin;
  final num hmax;
  final num flowPerNozzle;
  const FryerMatch({required this.group, required this.nozzle, required this.tag, required this.hmin, required this.hmax, required this.flowPerNozzle});
}

class FryerCalcResult {
  final bool ok;
  final List<FryerMatch> matches;
  final int modules;
  final num totalArea;
  final bool overLimit;
  final bool needsModularization;
  const FryerCalcResult({required this.ok, required this.matches, required this.modules, this.totalArea = 0, this.overLimit = false, this.needsModularization = false});
}

FryerCalcResult calcFryer({
  required bool hasDripboard,
  required num frypotD,
  required num frypotL,
  num? overallD,
  num? overallL,
  dynamic modules,
  String fuel = 'gas',
}) {
  final mods = math.max(1, intOrDefault(modules, 1));
  final fd = frypotD, fl = frypotL;
  final od = hasDripboard ? (overallD ?? 0) : fd;
  final ol = hasDripboard ? (overallL ?? 0) : fl;

  final matches = <FryerMatch>[];
  for (final g in kFryerGroups) {
    if (g.electric && fuel != 'electric') continue;
    if (!fitsBox(fd, fl, g.frypot[0], g.frypot[1])) continue;
    if (hasDripboard && !fitsBox(od, ol, g.overall[0], g.overall[1])) continue;
    for (final opt in g.opts) {
      matches.add(FryerMatch(group: g.id, nozzle: opt.nozzle, tag: opt.tag, hmin: opt.hmin, hmax: opt.hmax, flowPerNozzle: nozzleFlow(opt.nozzle)));
    }
  }
  matches.sort((a, b) {
    final c = a.flowPerNozzle.compareTo(b.flowPerNozzle);
    return c != 0 ? c : a.hmax.compareTo(b.hmax);
  });

  final totalArea = (hasDripboard ? od * ol : fd * fl) * mods;
  final overLimit = totalArea > kFryerMaxTotalArea;

  return FryerCalcResult(
    ok: matches.isNotEmpty && !overLimit,
    matches: matches,
    modules: mods,
    totalArea: totalArea,
    overLimit: overLimit,
    needsModularization: matches.isEmpty,
  );
}

// Sartén de volteo / Braising pan (pág. 4-13): mismas cajas "overall" de
// Table 4-4, SIN el límite de 864 in² que sí aplica a freidoras.
FryerCalcResult calcTiltSkillet(num d1, num d2, dynamic modules) {
  final mods = math.max(1, intOrDefault(modules, 1));
  final matches = <FryerMatch>[];
  for (final g in kFryerGroups) {
    if (g.electric) continue;
    if (!fitsBox(d1, d2, g.overall[0], g.overall[1])) continue;
    for (final opt in g.opts) {
      matches.add(FryerMatch(group: g.id, nozzle: opt.nozzle, tag: opt.tag, hmin: opt.hmin, hmax: opt.hmax, flowPerNozzle: nozzleFlow(opt.nozzle)));
    }
  }
  matches.sort((a, b) {
    final c = a.flowPerNozzle.compareTo(b.flowPerNozzle);
    return c != 0 ? c : a.hmax.compareTo(b.hmax);
  });
  return FryerCalcResult(ok: matches.isNotEmpty, matches: matches, modules: mods);
}

EquipmentResult? fryerResultForChoice(FryerCalcResult calc, int chosenIndex) {
  if (chosenIndex < 0 || chosenIndex >= calc.matches.length) return null;
  final m = calc.matches[chosenIndex];
  final qty = calc.modules;
  return EquipmentResult(
    nozzles: [NozzleQty(code: m.nozzle, qty: qty)],
    flowNumber: m.flowPerNozzle * qty,
    heightRange: '${m.hmin} in a ${m.hmax} in',
    detail: '${m.tag} — grupo ${m.group}${qty > 1 ? ' — $qty módulos' : ''}',
  );
}

EquipmentResult? tiltSkilletResultForChoice(FryerCalcResult calc, int chosenIndex) => fryerResultForChoice(calc, chosenIndex);

// ---------- Genérico "lado largo + área" (rango, plancha) -----------------
class LongSideMatch {
  final String nozzle;
  final int qty;
  final String tag;
  final num hmin;
  final num hmax;
  final num longSide;
  final num area;
  const LongSideMatch({required this.nozzle, required this.qty, required this.tag, required this.hmin, required this.hmax, required this.longSide, required this.area});
}

class LongSideCalcResult {
  final bool ok;
  final List<LongSideMatch> matches;
  final int modules;
  const LongSideCalcResult({required this.ok, required this.matches, required this.modules});
}

LongSideCalcResult calcLongSideArea(List<LongSideAreaOption> options, num d1, num d2, dynamic modules) {
  final mods = math.max(1, intOrDefault(modules, 1));
  final matches = options
      .where((o) => fitsLongSideArea(d1, d2, o.longSide, o.area))
      .map((o) => LongSideMatch(nozzle: o.nozzle, qty: o.qty, tag: o.tag, hmin: o.hmin, hmax: o.hmax, longSide: o.longSide, area: o.area))
      .toList();
  matches.sort((a, b) {
    final c = (a.qty * nozzleFlow(a.nozzle)).compareTo(b.qty * nozzleFlow(b.nozzle));
    return c != 0 ? c : a.hmax.compareTo(b.hmax);
  });
  return LongSideCalcResult(ok: matches.isNotEmpty, matches: matches, modules: mods);
}

EquipmentResult? longSideAreaResultForChoice(LongSideCalcResult calc, int chosenIdx) {
  if (chosenIdx < 0 || chosenIdx >= calc.matches.length) return null;
  final m = calc.matches[chosenIdx];
  final totalQty = m.qty * calc.modules;
  return EquipmentResult(
    nozzles: [NozzleQty(code: m.nozzle, qty: totalQty)],
    flowNumber: nozzleFlow(m.nozzle) * totalQty,
    heightRange: '${m.hmin} in a ${m.hmax} in',
    detail: '${m.tag}${calc.modules > 1 ? ' — ${calc.modules} módulos' : ''}',
  );
}

// ---------- Parrillas / asadores (Grill) -----------------------------------
class GrillMatch {
  final String nozzle;
  final int qty;
  final String tag;
  final num hmin;
  final num hmax;
  final num longSide;
  final num area;
  final num? maxDepth;
  const GrillMatch({required this.nozzle, required this.qty, required this.tag, required this.hmin, required this.hmax, required this.longSide, required this.area, this.maxDepth});
}

class GrillCalcResult {
  final bool ok;
  final List<GrillMatch> matches;
  final String fuel;
  const GrillCalcResult({required this.ok, required this.matches, required this.fuel});
}

GrillCalcResult calcGrill(String fuel, num d1, num d2, num? depth) {
  final matches = kGrillVariants
      .where((v) => v.fuels.contains(fuel))
      .where((v) => fitsLongSideArea(d1, d2, v.longSide, v.area))
      .where((v) => v.maxDepth == null || depth == null || depth <= v.maxDepth!)
      .map((v) => GrillMatch(nozzle: v.nozzle, qty: v.qty, tag: v.tag, hmin: v.hmin, hmax: v.hmax, longSide: v.longSide, area: v.area, maxDepth: v.maxDepth))
      .toList();
  matches.sort((a, b) {
    final c = (a.qty * nozzleFlow(a.nozzle)).compareTo(b.qty * nozzleFlow(b.nozzle));
    return c != 0 ? c : a.hmax.compareTo(b.hmax);
  });
  return GrillCalcResult(ok: matches.isNotEmpty, matches: matches, fuel: fuel);
}

EquipmentResult? grillResultForChoice(GrillCalcResult calc, int chosenIdx) {
  if (chosenIdx < 0 || chosenIdx >= calc.matches.length) return null;
  final m = calc.matches[chosenIdx];
  return EquipmentResult(
    nozzles: [NozzleQty(code: m.nozzle, qty: m.qty)],
    flowNumber: nozzleFlow(m.nozzle) * m.qty,
    heightRange: '${m.hmin} in a ${m.hmax} in',
    detail: '${m.tag} (${kFuelLabels[calc.fuel] ?? calc.fuel})',
  );
}

// ---------- Wok ------------------------------------------------------------
class WokMatch {
  final String nozzle;
  final int qty;
  final num diamMin;
  final num diamMax;
  final num depthMin;
  final num depthMax;
  final num hmin;
  final num hmax;
  const WokMatch({required this.nozzle, required this.qty, required this.diamMin, required this.diamMax, required this.depthMin, required this.depthMax, required this.hmin, required this.hmax});
}

class WokCalcResult {
  final bool ok;
  final List<WokMatch> matches;
  const WokCalcResult({required this.ok, required this.matches});
}

WokCalcResult calcWok(num diam, num depth) {
  final matches = kWokOptions
      .where((o) => diam >= o.diamMin && diam <= o.diamMax && depth >= o.depthMin && depth <= o.depthMax)
      .map((o) => WokMatch(nozzle: o.nozzle, qty: o.qty, diamMin: o.diamMin, diamMax: o.diamMax, depthMin: o.depthMin, depthMax: o.depthMax, hmin: o.hmin, hmax: o.hmax))
      .toList();
  matches.sort((a, b) => nozzleFlow(a.nozzle).compareTo(nozzleFlow(b.nozzle)));
  return WokCalcResult(ok: matches.isNotEmpty, matches: matches);
}

EquipmentResult wokResult(WokMatch opt) {
  return EquipmentResult(
    nozzles: [NozzleQty(code: opt.nozzle, qty: opt.qty)],
    flowNumber: nozzleFlow(opt.nozzle) * opt.qty,
    heightRange: '${opt.hmin} in a ${opt.hmax} in',
    detail: 'Wok ${opt.nozzle}',
  );
}

// ---------- Asador de cadena (chain broiler) -------------------------------
class ChainBroilerCalcResult {
  final bool ok;
  final ChainBroilerOption opt;
  final String? ratioWarning;
  final EquipmentResult? result;
  const ChainBroilerCalcResult({required this.ok, required this.opt, this.ratioWarning, this.result});
}

ChainBroilerCalcResult calcChainBroiler(String kind, num length, num width, num? openingL, num? openingW) {
  final opt = kChainBroilerOptions[kind]!;
  final fits = length <= opt.maxLength && width <= opt.maxWidth;
  String? ratioWarning;
  if (kind == 'overhead' && openingL != null && openingW != null && openingL > 0 && openingW > 0) {
    final minL = length * (opt.minOpeningRatio ?? 0), minW = width * (opt.minOpeningRatio ?? 0);
    final minOpening = opt.minOpening ?? 0;
    if (openingL < math.max(minL, minOpening) || openingW < math.max(minW, minOpening)) {
      ratioWarning = 'La abertura no cumple el mínimo de 60% de las dimensiones internas (o 12x12 in mínimo). Verifique protección horizontal en su lugar.';
    }
  }
  return ChainBroilerCalcResult(
    ok: fits,
    opt: opt,
    ratioWarning: ratioWarning,
    result: fits
        ? EquipmentResult(
            nozzles: [NozzleQty(code: opt.nozzle, qty: opt.qty)],
            flowNumber: nozzleFlow(opt.nozzle) * opt.qty,
            heightRange: '${opt.hmin} in a ${opt.hmax} in',
            detail: opt.label,
          )
        : null,
  );
}

// ---------- Asador vertical / salamandra -----------------------------------
class UprightBroilerCalcResult {
  final bool ok;
  final EquipmentResult? result;
  const UprightBroilerCalcResult({required this.ok, this.result});
}

UprightBroilerCalcResult calcUprightBroiler(num length, num width) {
  final fits = length <= kUprightBroiler.maxLength && width <= kUprightBroiler.maxWidth;
  return UprightBroilerCalcResult(
    ok: fits,
    result: fits
        ? EquipmentResult(
            nozzles: [NozzleQty(code: kUprightBroiler.nozzle, qty: kUprightBroiler.qty)],
            flowNumber: nozzleFlow(kUprightBroiler.nozzle) * kUprightBroiler.qty,
            heightRange: '—',
            detail: kUprightBroiler.label,
          )
        : null,
  );
}

class SalamanderCalcResult {
  final bool ok;
  final List<SalamanderOption> matches;
  const SalamanderCalcResult({required this.ok, required this.matches});
}

SalamanderCalcResult calcSalamander(num length, num width) {
  final matches = kSalamanderOptions.where((o) => length <= o.maxLength && width <= o.maxWidth).toList();
  return SalamanderCalcResult(ok: matches.isNotEmpty, matches: matches);
}

EquipmentResult salamanderResult(SalamanderOption opt) {
  return EquipmentResult(
    nozzles: [NozzleQty(code: opt.nozzle, qty: opt.qty)],
    flowNumber: nozzleFlow(opt.nozzle) * opt.qty,
    heightRange: '—',
    detail: opt.label,
  );
}

// ---------- Ducto -----------------------------------------------------------
class DuctCalcResult {
  final bool ok;
  final bool needsManual;
  final String? msg;
  final EquipmentResult? result;
  final bool estimated;
  const DuctCalcResult({required this.ok, this.needsManual = false, this.msg, this.result, this.estimated = false});
}

EquipmentResult _ductRes(List<NozzleQty> nozzles, String detail) {
  final flowNumber = nozzles.fold<num>(0, (s, n) => s + nozzleFlow(n.code) * n.qty);
  return EquipmentResult(nozzles: nozzles, flowNumber: flowNumber, detail: detail, heightRange: '2 a 8 in dentro de la abertura del ducto');
}

DuctCalcResult _scaleDuctByQty(DuctCalcResult base, int qty) {
  if (!base.ok || base.result == null || qty <= 1) return base;
  final r = base.result!;
  final nozzles = r.nozzles.map((n) => NozzleQty(code: n.code, qty: n.qty * qty)).toList();
  final flowNumber = r.flowNumber * qty;
  return DuctCalcResult(
    ok: true,
    result: EquipmentResult(nozzles: nozzles, flowNumber: flowNumber, heightRange: r.heightRange, detail: '${r.detail} — × $qty ductos'),
    estimated: base.estimated,
  );
}

// qty = número de ductos idénticos (todas las boquillas resultantes se
// multiplican por esta cantidad).
DuctCalcResult calcDuct(num? perimeter, num? diameter, bool isRound, dynamic qtyIn) {
  final qty = math.max(1, intOrDefault(qtyIn, 1));
  DuctCalcResult base;
  if (isRound) {
    final d = diameter ?? 0;
    if (d <= kDuctSingle1W.maxDiameter) {
      base = DuctCalcResult(ok: true, result: _ductRes([const NozzleQty(code: '1W', qty: 1)], 'Ducto redondo — 1W (una boquilla)'));
    } else if (d <= kDuctSingle2W.maxDiameter) {
      base = DuctCalcResult(ok: true, result: _ductRes([const NozzleQty(code: '2W', qty: 1)], 'Ducto redondo — 2W (una boquilla)'));
    } else {
      return const DuctCalcResult(ok: false, needsManual: true, msg: 'Ducto redondo mayor a 32 in de diámetro: no hay opción redonda estándar, requiere diseño especial (consulte a ANSUL).');
    }
  } else {
    final p = perimeter ?? 0;
    if (p <= kDuctSingle1W.maxPerimeter) {
      base = DuctCalcResult(ok: true, result: _ductRes([const NozzleQty(code: '1W', qty: 1)], 'Ducto — boquilla única 1W'));
    } else if (p <= kDuctSingle2W.maxPerimeter) {
      base = DuctCalcResult(ok: true, result: _ductRes([const NozzleQty(code: '2W', qty: 1)], 'Ducto — boquilla única 2W'));
    } else if (p <= kDuctDual.maxPerimeter) {
      base = DuctCalcResult(ok: true, result: _ductRes([const NozzleQty(code: '1W', qty: 1), const NozzleQty(code: '2W', qty: 1)], 'Ducto — opción de tres flujos (1W + 2W)'));
    } else {
      // > 135 in perímetro: aproximación conservadora usando módulos 2W
      // (~35 in de lado B por módulo), redondeado a número par.
      final approxNozzlesPerRow = (p / 2 / 35).ceil();
      final nozzles = math.max(4, approxNozzlesPerRow * 2);
      base = DuctCalcResult(
        ok: true,
        estimated: true,
        result: EquipmentResult(
          nozzles: [NozzleQty(code: '2W', qty: nozzles)],
          flowNumber: nozzleFlow('2W') * nozzles,
          heightRange: '2 a 8 in dentro de la abertura del ducto',
          detail: 'Ducto grande (perímetro > 135 in) — ESTIMACIÓN conservadora de $nozzles boquillas 2W por ducto. Verifique manualmente contra las Gráficas 4-1/4-2 del manual R-102 o consulte a ANSUL antes de instalar.',
        ),
      );
    }
  }
  return _scaleDuctByQty(base, qty);
}

// ---------- Precipitador electrostático -------------------------------------
EquipmentResult calcPrecipitator(dynamic cellsIn) {
  final qty = math.max(1, intOrDefault(cellsIn, 1));
  return EquipmentResult(
    nozzles: [NozzleQty(code: '1/2N', qty: qty)],
    flowNumber: nozzleFlow('1/2N') * qty,
    detail: 'Precipitador electrostático — 1/2N por celda ($qty celdas)',
  );
}

// ---------- Pleno -------------------------------------------------------------
// plenumQty = número de plenos idénticos.
EquipmentResult calcPlenum(String kind, num lengthFt, dynamic plenumQtyIn) {
  final plenumQty = math.max(1, intOrDefault(plenumQtyIn, 1));
  final opt = kPlenumOptions[kind]!;
  final nozzlePairs = (lengthFt / opt.coveragePerNozzleFt).ceil();
  final qty = nozzlePairs * opt.qty;
  final base = EquipmentResult(
    nozzles: [NozzleQty(code: opt.nozzle, qty: qty)],
    flowNumber: nozzleFlow(opt.nozzle) * qty,
    detail: '${opt.label} — $lengthFt ft',
  );
  if (plenumQty <= 1) return base;
  final nozzles = base.nozzles.map((n) => NozzleQty(code: n.code, qty: n.qty * plenumQty)).toList();
  return EquipmentResult(nozzles: nozzles, flowNumber: base.flowNumber * plenumQty, detail: '${base.detail} — × $plenumQty plenos');
}
