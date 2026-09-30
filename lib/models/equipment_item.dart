import 'calc_result.dart';

/// Referencia a la entrada de catálogo usada por un equipo (si el usuario
/// eligió una marca/modelo en vez de capturar medidas). Puerto de
/// formState.catalogRef en app2.js.
class CatalogRef {
  final String brand;
  final String model;
  final String notes;
  final num? hmin;
  final num? hmax;
  final num? surfaceW;
  final num? surfaceD;
  final String? fuel;
  final bool hasFixedNozzles;
  final String source; // 'manual' | 'user'

  const CatalogRef({
    required this.brand,
    required this.model,
    this.notes = '',
    this.hmin,
    this.hmax,
    this.surfaceW,
    this.surfaceD,
    this.fuel,
    required this.hasFixedNozzles,
    this.source = 'manual',
  });

  factory CatalogRef.fromJson(Map<String, dynamic> j) => CatalogRef(
        brand: (j['brand'] as String?) ?? '',
        model: (j['model'] as String?) ?? '',
        notes: (j['notes'] as String?) ?? '',
        hmin: j['hmin'] as num?,
        hmax: j['hmax'] as num?,
        surfaceW: j['surfaceW'] as num?,
        surfaceD: j['surfaceD'] as num?,
        fuel: j['fuel'] as String?,
        hasFixedNozzles: (j['hasFixedNozzles'] as bool?) ?? false,
        source: (j['source'] as String?) ?? 'manual',
      );

  Map<String, dynamic> toJson() => {
        'brand': brand,
        'model': model,
        'notes': notes,
        'hmin': hmin,
        'hmax': hmax,
        'surfaceW': surfaceW,
        'surfaceD': surfaceD,
        'fuel': fuel,
        'hasFixedNozzles': hasFixedNozzles,
        'source': source,
      };
}

/// Un equipo/ducto/pleno guardado dentro de una cocina. Puerto del objeto
/// `item` que la app web guarda en kitchen.equipment[].
class EquipmentItem {
  final String id;
  final String category;
  final String brand;
  final String model;
  final String notes;
  /// Valores capturados en el formulario (equivalente a formState.fields):
  /// claves como frypotD, frypotL, fuel, hasDripboard, modules, etc.
  final Map<String, dynamic> input;
  final int chosenIdx;
  final CatalogRef? catalogRef;
  final EquipmentResult? result;
  final int createdAt;

  const EquipmentItem({
    required this.id,
    required this.category,
    this.brand = '',
    this.model = '',
    this.notes = '',
    this.input = const {},
    this.chosenIdx = 0,
    this.catalogRef,
    this.result,
    required this.createdAt,
  });

  EquipmentItem copyWith({
    String? category,
    String? brand,
    String? model,
    String? notes,
    Map<String, dynamic>? input,
    int? chosenIdx,
    CatalogRef? catalogRef,
    bool clearCatalogRef = false,
    EquipmentResult? result,
  }) {
    return EquipmentItem(
      id: id,
      category: category ?? this.category,
      brand: brand ?? this.brand,
      model: model ?? this.model,
      notes: notes ?? this.notes,
      input: input ?? this.input,
      chosenIdx: chosenIdx ?? this.chosenIdx,
      catalogRef: clearCatalogRef ? null : (catalogRef ?? this.catalogRef),
      result: result ?? this.result,
      createdAt: createdAt,
    );
  }

  factory EquipmentItem.fromJson(Map<String, dynamic> j) => EquipmentItem(
        id: j['id'] as String,
        category: j['category'] as String,
        brand: (j['brand'] as String?) ?? '',
        model: (j['model'] as String?) ?? '',
        notes: (j['notes'] as String?) ?? '',
        input: Map<String, dynamic>.from(j['input'] as Map? ?? {}),
        chosenIdx: (j['chosenIdx'] as num?)?.toInt() ?? 0,
        catalogRef: j['catalogRef'] != null ? CatalogRef.fromJson(j['catalogRef'] as Map<String, dynamic>) : null,
        result: j['result'] != null ? EquipmentResult.fromJson(j['result'] as Map<String, dynamic>) : null,
        createdAt: (j['createdAt'] as num?)?.toInt() ?? 0,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'category': category,
        'brand': brand,
        'model': model,
        'notes': notes,
        'input': input,
        'chosenIdx': chosenIdx,
        if (catalogRef != null) 'catalogRef': catalogRef!.toJson(),
        if (result != null) 'result': result!.toJson(),
        'createdAt': createdAt,
      };

  /// Etiqueta mostrada para un equipo ya guardado (agrega el número de
  /// quemadores para estufas). Puerto de categoryDisplayLabel() en app.js.
  String displayLabel(Map<String, String> categoryLabels) {
    if (category == 'range' && input['burners'] != null) {
      final b = input['burners'];
      return 'Estufa $b Quemadores / Range $b Burner';
    }
    return categoryLabels[category] ?? category;
  }
}
