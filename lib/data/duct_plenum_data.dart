// Ductos (pág. 4-1 a 4-3) y plenos (pág. 4-5 a 4-7). Puerto directo de
// data.js -> DUCT_OPTIONS / PLENUM_OPTIONS.
class DuctSingleOption {
  final String nozzle;
  final int qty;
  final num maxPerimeter;
  final num maxDiameter;
  const DuctSingleOption({required this.nozzle, required this.qty, required this.maxPerimeter, required this.maxDiameter});
}

class DuctDualOption {
  final List<String> nozzleCodes; // ['1W','2W']
  final num maxPerimeter;
  const DuctDualOption({required this.nozzleCodes, required this.maxPerimeter});
}

const kDuctSingle1W = DuctSingleOption(nozzle: '1W', qty: 1, maxPerimeter: 50, maxDiameter: 16);
const kDuctSingle2W = DuctSingleOption(nozzle: '2W', qty: 1, maxPerimeter: 100, maxDiameter: 32);
const kDuctDual = DuctDualOption(nozzleCodes: ['1W', '2W'], maxPerimeter: 135);

class PlenumOption {
  final String nozzle;
  final int qty;
  final num coveragePerNozzleFt;
  final String label;
  const PlenumOption({required this.nozzle, required this.qty, required this.coveragePerNozzleFt, required this.label});
}

const Map<String, PlenumOption> kPlenumOptions = {
  'vertical1W': PlenumOption(nozzle: '1W', qty: 1, coveragePerNozzleFt: 4, label: 'Vertical, 1W (4 ft por boquilla)'),
  'horizV1W': PlenumOption(nozzle: '1W', qty: 1, coveragePerNozzleFt: 6, label: 'Horizontal banco "V", 1W (6 ft por boquilla)'),
  'horizSingle1N': PlenumOption(nozzle: '1N', qty: 1, coveragePerNozzleFt: 10, label: 'Horizontal banco sencillo, 1N (10 ft por boquilla)'),
  'horizVbank1N': PlenumOption(nozzle: '1N', qty: 2, coveragePerNozzleFt: 10, label: 'Horizontal banco "V", 1N (2 boquillas cada 10 ft)'),
};
