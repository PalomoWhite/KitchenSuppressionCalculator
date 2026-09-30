import 'calc_result.dart';

/// Modelo de una entrada del catálogo de equipos por marca/modelo — ya sea
/// del manual ANSUL R-102 (assets/model_catalog.json, source: 'manual') o
/// agregada por el propio usuario (guardada en el almacenamiento local,
/// source: 'user').
class CatalogEntry {
  final String? id; // solo entradas de usuario
  final String category;
  final String brand;
  final String model;
  final String? fuel;
  final List<NozzleQty>? nozzles; // null = sin boquillas fijas (solo referencia)
  final num? hmin;
  final num? hmax;
  final num? surfaceW;
  final num? surfaceD;
  final String notes;
  final String source; // 'manual' | 'user'
  final int? createdAt;

  const CatalogEntry({
    this.id,
    required this.category,
    required this.brand,
    required this.model,
    this.fuel,
    this.nozzles,
    this.hmin,
    this.hmax,
    this.surfaceW,
    this.surfaceD,
    this.notes = '',
    this.source = 'manual',
    this.createdAt,
  });

  factory CatalogEntry.fromJson(Map<String, dynamic> j, {required String source}) {
    final nozzlesRaw = j['nozzles'];
    return CatalogEntry(
      id: j['id'] as String?,
      category: j['category'] as String,
      brand: (j['brand'] as String?) ?? '',
      model: (j['model'] as String?) ?? '',
      fuel: j['fuel'] as String?,
      nozzles: nozzlesRaw == null ? null : (nozzlesRaw as List).map((e) => NozzleQty.fromJson(e as Map<String, dynamic>)).toList(),
      hmin: j['hmin'] as num?,
      hmax: j['hmax'] as num?,
      surfaceW: j['surfaceW'] as num?,
      surfaceD: j['surfaceD'] as num?,
      notes: (j['notes'] as String?) ?? '',
      source: source,
      createdAt: j['createdAt'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        'category': category,
        'brand': brand,
        'model': model,
        'fuel': fuel,
        'nozzles': nozzles?.map((n) => n.toJson()).toList(),
        'hmin': hmin,
        'hmax': hmax,
        'surfaceW': surfaceW,
        'surfaceD': surfaceD,
        'notes': notes,
        if (createdAt != null) 'createdAt': createdAt,
      };

  CatalogEntry copyWith({
    String? id,
    String? category,
    String? brand,
    String? model,
    String? fuel,
    List<NozzleQty>? nozzles,
    bool clearNozzles = false,
    num? hmin,
    num? hmax,
    num? surfaceW,
    num? surfaceD,
    String? notes,
    String? source,
    int? createdAt,
  }) {
    return CatalogEntry(
      id: id ?? this.id,
      category: category ?? this.category,
      brand: brand ?? this.brand,
      model: model ?? this.model,
      fuel: fuel ?? this.fuel,
      nozzles: clearNozzles ? null : (nozzles ?? this.nozzles),
      hmin: hmin ?? this.hmin,
      hmax: hmax ?? this.hmax,
      surfaceW: surfaceW ?? this.surfaceW,
      surfaceD: surfaceD ?? this.surfaceD,
      notes: notes ?? this.notes,
      source: source ?? this.source,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

/// Nombres bilingües (Español / English) — mismo orden que el catálogo del
/// manual R-102. Puerto directo de app.js -> CATEGORY_LABELS.
const Map<String, String> kCategoryLabels = {
  'fryer': 'Freidora / Fryer',
  'tiltskillet': 'Sartén de Volteo / Tilting Skillet',
  'range': 'Estufa / Range',
  'griddle': 'Plancha / Griddle',
  'grill': 'Parrilla / Grill',
  'naturalcharcoal': 'Asador Carbón / Natural Charcoal Grill',
  'woodgrill': 'Asador Leña / Wood Fuel Grill',
  'chainbroiler': 'Asador de Cadena / Chain Broiler',
  'uprightbroiler': 'Asador Vertical / Upright Broiler',
  'salamander': 'Salamandra / Cheesemelter',
  'wok': 'Wok / Wok',
  'combioven': 'Horno Combi / Combi Oven',
  'marmita': 'Marmita / Steam Kettle',
  'duct': 'Ducto / Duct',
  'plenum': 'Pleno / Plenum',
  'precipitator': 'Precipitador Electrostático / Electrostatic Precipitator',
};

/// Categorías renombradas en versiones anteriores de la app web — se
/// conserva el mismo mapa de migración por si se importa un respaldo viejo.
const Map<String, String> kLegacyCategoryMap = {'charbroiler': 'chainbroiler'};

/// Categorías que sí se pueden agregar al catálogo de usuario (excluye
/// ducto/pleno/precipitador, que no dependen de marca/modelo).
const List<String> kCatalogCategories = [
  'fryer', 'tiltskillet', 'range', 'griddle', 'grill', 'naturalcharcoal',
  'woodgrill', 'chainbroiler', 'uprightbroiler', 'salamander', 'wok', 'combioven', 'marmita',
];
