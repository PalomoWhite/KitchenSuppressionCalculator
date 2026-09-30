// Puerto directo de data.js -> WOK_OPTIONS.
class WokOption {
  final String nozzle;
  final int qty;
  final num diamMin;
  final num diamMax;
  final num depthMin;
  final num depthMax;
  final num hmin;
  final num hmax;
  const WokOption({
    required this.nozzle,
    required this.qty,
    required this.diamMin,
    required this.diamMax,
    required this.depthMin,
    required this.depthMax,
    required this.hmin,
    required this.hmax,
  });
}

const List<WokOption> kWokOptions = [
  WokOption(nozzle: '260', qty: 1, diamMin: 14, diamMax: 30, depthMin: 3.75, depthMax: 8, hmin: 35, hmax: 45),
  WokOption(nozzle: '1N', qty: 1, diamMin: 11, diamMax: 24, depthMin: 3, depthMax: 6, hmin: 30, hmax: 40),
];
