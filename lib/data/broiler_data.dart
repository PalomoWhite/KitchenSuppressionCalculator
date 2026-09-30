// Asadores de cadena, verticales y salamandras. Puerto directo de data.js ->
// CHAIN_BROILER_OPTIONS / UPRIGHT_BROILER / SALAMANDER_OPTIONS.
class ChainBroilerOption {
  final String nozzle;
  final int qty;
  final num maxLength;
  final num maxWidth;
  final num hmin;
  final num hmax;
  final String label;
  final num? minOpeningRatio;
  final num? minOpening;
  const ChainBroilerOption({
    required this.nozzle,
    required this.qty,
    required this.maxLength,
    required this.maxWidth,
    required this.hmin,
    required this.hmax,
    required this.label,
    this.minOpeningRatio,
    this.minOpening,
  });
}

const Map<String, ChainBroilerOption> kChainBroilerOptions = {
  'horizontal': ChainBroilerOption(nozzle: '1N', qty: 2, maxLength: 43, maxWidth: 31, hmin: 1, hmax: 3, label: 'Horizontal (2 boquillas 1N)'),
  'overhead': ChainBroilerOption(nozzle: '1W', qty: 2, maxLength: 32, maxWidth: 34, hmin: 10, hmax: 26, label: 'Cenital / overhead (2 boquillas 1W)', minOpeningRatio: 0.6, minOpening: 12),
};

class UprightBroilerSpec {
  final String nozzle;
  final int qty;
  final num maxLength;
  final num maxWidth;
  final String label;
  const UprightBroilerSpec({required this.nozzle, required this.qty, required this.maxLength, required this.maxWidth, required this.label});
}

const kUprightBroiler = UprightBroilerSpec(nozzle: '1/2N', qty: 2, maxLength: 32.5, maxWidth: 30, label: 'Asador vertical / Salamandra (2 boquillas 1/2N)');

class SalamanderOption {
  final String id;
  final String nozzle;
  final int qty;
  final num maxLength;
  final num maxWidth;
  final String label;
  const SalamanderOption({required this.id, required this.nozzle, required this.qty, required this.maxLength, required this.maxWidth, required this.label});
}

const List<SalamanderOption> kSalamanderOptions = [
  SalamanderOption(id: 'overhead1N', nozzle: '1N', qty: 1, maxLength: 29, maxWidth: 16, label: 'Cenital 1N (6-12 in al frente, 0-12 in de altura)'),
  SalamanderOption(id: 'overhead1F', nozzle: '1F', qty: 1, maxLength: 31, maxWidth: 15, label: 'Cenital 1F (8-12 in al frente, 12-18 in de altura)'),
  SalamanderOption(id: 'local1N', nozzle: '1N', qty: 1, maxLength: 31, maxWidth: 15, label: 'Lateral / local 1N (montada al costado)'),
];
