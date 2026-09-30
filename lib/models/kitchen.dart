import 'equipment_item.dart';

class ReportMeta {
  final String? responsible;
  final String? date;
  const ReportMeta({this.responsible, this.date});
  factory ReportMeta.fromJson(Map<String, dynamic> j) => ReportMeta(responsible: j['responsible'] as String?, date: j['date'] as String?);
  Map<String, dynamic> toJson() => {'responsible': responsible, 'date': date};
}

class Kitchen {
  final String id;
  final String name;
  final int createdAt;
  final List<EquipmentItem> equipment;
  final ReportMeta? reportMeta;

  const Kitchen({required this.id, required this.name, required this.createdAt, this.equipment = const [], this.reportMeta});

  Kitchen copyWith({String? name, List<EquipmentItem>? equipment, ReportMeta? reportMeta}) => Kitchen(
        id: id,
        name: name ?? this.name,
        createdAt: createdAt,
        equipment: equipment ?? this.equipment,
        reportMeta: reportMeta ?? this.reportMeta,
      );

  factory Kitchen.fromJson(Map<String, dynamic> j) => Kitchen(
        id: j['id'] as String,
        name: (j['name'] as String?) ?? 'Cocina sin nombre',
        createdAt: (j['createdAt'] as num?)?.toInt() ?? 0,
        equipment: ((j['equipment'] as List?) ?? []).map((e) => EquipmentItem.fromJson(e as Map<String, dynamic>)).toList(),
        reportMeta: j['reportMeta'] != null ? ReportMeta.fromJson(j['reportMeta'] as Map<String, dynamic>) : null,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'createdAt': createdAt,
        'equipment': equipment.map((e) => e.toJson()).toList(),
        if (reportMeta != null) 'reportMeta': reportMeta!.toJson(),
      };
}
