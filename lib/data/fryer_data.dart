// Freidoras: grupos de tamaño máximo (Tabla 4-2, 4-3 y Nozzle Application
// Chart, pág. 4-7 a 4-11 y 4-29/4-30). Puerto directo de data.js -> FRYER_GROUPS.
class FryerNozzleOpt {
  final String nozzle;
  final num hmin;
  final num hmax;
  final String tag;
  const FryerNozzleOpt({required this.nozzle, required this.hmin, required this.hmax, required this.tag});
}

class FryerGroup {
  final String id;
  final List<num> frypot; // [d, l]
  final List<num> overall; // [d, l]
  final bool electric;
  final List<FryerNozzleOpt> opts;
  const FryerGroup({required this.id, required this.frypot, required this.overall, this.electric = false, required this.opts});
}

const List<FryerGroup> kFryerGroups = [
  FryerGroup(id: 'A', frypot: [14, 15], overall: [14, 21], opts: [
    FryerNozzleOpt(nozzle: '290', hmin: 13, hmax: 16, tag: 'Baja proximidad'),
  ]),
  FryerGroup(id: 'B', frypot: [14.5, 14], overall: [14.5, 26.5], opts: [
    FryerNozzleOpt(nozzle: '290', hmin: 16, hmax: 27, tag: 'Media proximidad'),
  ]),
  FryerGroup(id: 'C', frypot: [15, 14], overall: [21, 14], opts: [
    FryerNozzleOpt(nozzle: '230', hmin: 27, hmax: 47, tag: 'Alta proximidad'),
    FryerNozzleOpt(nozzle: '245', hmin: 20, hmax: 27, tag: 'Media proximidad'),
  ]),
  FryerGroup(id: 'D', frypot: [19.5, 19], overall: [25.375, 19.5], opts: [
    FryerNozzleOpt(nozzle: '3N', hmin: 21, hmax: 34, tag: 'Alta proximidad'),
    FryerNozzleOpt(nozzle: '290', hmin: 13, hmax: 16, tag: 'Baja proximidad'),
  ]),
  FryerGroup(id: 'E', frypot: [18, 18], overall: [18, 27.75], opts: [
    FryerNozzleOpt(nozzle: '3N', hmin: 25, hmax: 35, tag: 'Alta proximidad'),
  ]),
  FryerGroup(id: 'F', frypot: [14.5, 16.5], overall: [14.5, 26.5], opts: [
    FryerNozzleOpt(nozzle: '290', hmin: 16, hmax: 21, tag: 'Alta proximidad'),
  ]),
  FryerGroup(id: 'G', frypot: [6.5, 17], overall: [14, 21], electric: true, opts: [
    FryerNozzleOpt(nozzle: '245', hmin: 21, hmax: 27, tag: 'Media proximidad (vat dividida eléctrica)'),
    FryerNozzleOpt(nozzle: '290', hmin: 16, hmax: 21, tag: 'Alta proximidad (vat dividida eléctrica)'),
  ]),
];

const num kFryerMaxTotalArea = 864; // in^2, límite absoluto para modularización
