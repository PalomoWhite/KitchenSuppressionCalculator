// Estructuras de resultado del motor de cálculo. Puerto de las formas que
// devuelven las funciones de calc.js (result objects con nozzles/flowNumber).
class NozzleQty {
  final String code;
  final int qty;
  const NozzleQty({required this.code, required this.qty});

  Map<String, dynamic> toJson() => {'code': code, 'qty': qty};
  factory NozzleQty.fromJson(Map<String, dynamic> j) => NozzleQty(code: j['code'] as String, qty: (j['qty'] as num).toInt());
}

/// El resultado final aplicado a un equipo guardado: boquillas + flow number
/// + altura de montaje + texto descriptivo. Equivalente al objeto `result`
/// que la app web guarda en cada equipo.
class EquipmentResult {
  final List<NozzleQty> nozzles;
  final num flowNumber;
  final String? heightRange;
  final String detail;
  const EquipmentResult({required this.nozzles, required this.flowNumber, this.heightRange, required this.detail});

  Map<String, dynamic> toJson() => {
        'nozzles': nozzles.map((n) => n.toJson()).toList(),
        'flowNumber': flowNumber,
        'heightRange': heightRange,
        'detail': detail,
      };
  factory EquipmentResult.fromJson(Map<String, dynamic> j) => EquipmentResult(
        nozzles: (j['nozzles'] as List).map((e) => NozzleQty.fromJson(e as Map<String, dynamic>)).toList(),
        flowNumber: (j['flowNumber'] as num?) ?? 0,
        heightRange: j['heightRange'] as String?,
        detail: (j['detail'] as String?) ?? '',
      );
}

/// Una opción candidata dentro de una lista de coincidencias que el usuario
/// puede elegir (equivalente a un elemento de `matches` en calc.js). No todas
/// las categorías usan todos los campos.
class CalcMatch {
  final String nozzle;
  final int qty; // boquillas por unidad (antes de multiplicar por módulos)
  final String tag;
  final num? hmin;
  final num? hmax;
  final String? group; // solo freidoras
  final num? longSide;
  final num? area;
  final num? maxDepth;

  const CalcMatch({
    required this.nozzle,
    this.qty = 1,
    required this.tag,
    this.hmin,
    this.hmax,
    this.group,
    this.longSide,
    this.area,
    this.maxDepth,
  });

  num flowPerNozzle(num Function(String) nozzleFlowFn) => nozzleFlowFn(nozzle);
}
