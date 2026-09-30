// Categorías con formato "lado más largo + área" (Nozzle Application Chart,
// pág. 4-29 a 4-31). Puerto directo de data.js -> RANGE_OPTIONS / GRIDDLE_OPTIONS.
class LongSideAreaOption {
  final String nozzle;
  final int qty;
  final num longSide;
  final num area;
  final num hmin;
  final num hmax;
  final String tag;
  const LongSideAreaOption({
    required this.nozzle,
    required this.qty,
    required this.longSide,
    required this.area,
    required this.hmin,
    required this.hmax,
    required this.tag,
  });
}

const List<LongSideAreaOption> kRangeOptions = [
  LongSideAreaOption(nozzle: '1N', qty: 1, longSide: 32, area: 384, hmin: 30, hmax: 40, tag: 'Alta proximidad'),
  LongSideAreaOption(nozzle: '1N', qty: 1, longSide: 24, area: 432, hmin: 15, hmax: 20, tag: 'Baja proximidad'),
  LongSideAreaOption(nozzle: '1F', qty: 1, longSide: 28, area: 336, hmin: 40, hmax: 48, tag: 'Con repisa trasera (backshelf)'),
  LongSideAreaOption(nozzle: '260', qty: 1, longSide: 32, area: 384, hmin: 30, hmax: 40, tag: 'Con repisa trasera (backshelf)'),
  LongSideAreaOption(nozzle: '245', qty: 1, longSide: 28, area: 672, hmin: 40, hmax: 50, tag: 'Alta proximidad'),
  LongSideAreaOption(nozzle: '260', qty: 1, longSide: 32, area: 768, hmin: 30, hmax: 40, tag: 'Media proximidad'),
  LongSideAreaOption(nozzle: '290', qty: 2, longSide: 36, area: 1008, hmin: 15, hmax: 20, tag: 'Baja proximidad (dos boquillas)'),
];

const List<LongSideAreaOption> kGriddleOptions = [
  LongSideAreaOption(nozzle: '260', qty: 1, longSide: 48, area: 1440, hmin: 30, hmax: 50, tag: 'Alta proximidad (perímetro)'),
  LongSideAreaOption(nozzle: '290', qty: 1, longSide: 30, area: 720, hmin: 30, hmax: 50, tag: 'Alta proximidad (centro)'),
  LongSideAreaOption(nozzle: '1N', qty: 1, longSide: 36, area: 1080, hmin: 35, hmax: 40, tag: 'Alta proximidad (perímetro)'),
  LongSideAreaOption(nozzle: '290', qty: 1, longSide: 48, area: 1440, hmin: 20, hmax: 30, tag: 'Media proximidad'),
  LongSideAreaOption(nozzle: '1W', qty: 1, longSide: 26, area: 533, hmin: 15, hmax: 20, tag: 'Baja proximidad'),
  LongSideAreaOption(nozzle: '2W', qty: 1, longSide: 36, area: 1080, hmin: 10, hmax: 20, tag: 'Baja proximidad'),
  LongSideAreaOption(nozzle: '2120', qty: 1, longSide: 48, area: 1440, hmin: 10, hmax: 20, tag: 'Baja proximidad'),
];
