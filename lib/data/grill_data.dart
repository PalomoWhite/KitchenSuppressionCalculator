// Variantes de parrilla/asador (Sección 4, pág. 4-24 a 4-27) filtradas por
// combustible. Puerto directo de data.js -> GRILL_VARIANTS / FUEL_LABELS.
class GrillVariant {
  final String key;
  final String nozzle;
  final int qty;
  final num longSide;
  final num area;
  final num hmin;
  final num hmax;
  final num? maxDepth;
  final num? maxLogDiameter;
  final List<String> fuels;
  final String tag;
  const GrillVariant({
    required this.key,
    required this.nozzle,
    required this.qty,
    required this.longSide,
    required this.area,
    required this.hmin,
    required this.hmax,
    this.maxDepth,
    this.maxLogDiameter,
    required this.fuels,
    required this.tag,
  });
}

const List<GrillVariant> kGrillVariants = [
  GrillVariant(key: 'gasRadiantElectric', nozzle: '1N', qty: 1, longSide: 36, area: 864, hmin: 15, hmax: 40, fuels: ['gas', 'electric'], tag: 'Gas-radiante / eléctrico combinado'),
  GrillVariant(key: 'electric', nozzle: '1N', qty: 1, longSide: 34, area: 680, hmin: 20, hmax: 50, fuels: ['electric'], tag: 'Eléctrico'),
  GrillVariant(key: 'lavaRock', nozzle: '1N', qty: 1, longSide: 24, area: 312, hmin: 18, hmax: 35, maxDepth: 4, fuels: ['gas'], tag: 'Lava / cerámica'),
  GrillVariant(key: 'lavaOrCharcoalAlt', nozzle: '3N', qty: 1, longSide: 30, area: 720, hmin: 14, hmax: 40, maxDepth: 4, fuels: ['gas', 'charcoal'], tag: 'Lava o carbón — mayor cobertura'),
  GrillVariant(key: 'naturalCharcoal', nozzle: '1N', qty: 1, longSide: 24, area: 288, hmin: 18, hmax: 40, maxDepth: 4, fuels: ['charcoal'], tag: 'Carbón natural'),
  GrillVariant(key: 'woodFueled', nozzle: '3N', qty: 1, longSide: 30, area: 720, hmin: 14, hmax: 40, maxDepth: 6, maxLogDiameter: 4, fuels: ['wood'], tag: 'Leña (mezquite)'),
];

const Map<String, String> kFuelLabels = {
  'gas': 'Gas',
  'electric': 'Eléctrico',
  'charcoal': 'Carbón',
  'wood': 'Leña',
};
