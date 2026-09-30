import 'kitchen.dart';

class Project {
  final String id;
  final String name;
  final int createdAt;
  final List<Kitchen> kitchens;
  final ReportMeta? reportMeta;

  const Project({required this.id, required this.name, required this.createdAt, this.kitchens = const [], this.reportMeta});

  Project copyWith({String? name, List<Kitchen>? kitchens, ReportMeta? reportMeta}) => Project(
        id: id,
        name: name ?? this.name,
        createdAt: createdAt,
        kitchens: kitchens ?? this.kitchens,
        reportMeta: reportMeta ?? this.reportMeta,
      );

  factory Project.fromJson(Map<String, dynamic> j) => Project(
        id: j['id'] as String,
        name: (j['name'] as String?) ?? 'Proyecto sin nombre',
        createdAt: (j['createdAt'] as num?)?.toInt() ?? 0,
        kitchens: ((j['kitchens'] as List?) ?? []).map((e) => Kitchen.fromJson(e as Map<String, dynamic>)).toList(),
        reportMeta: j['reportMeta'] != null ? ReportMeta.fromJson(j['reportMeta'] as Map<String, dynamic>) : null,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'createdAt': createdAt,
        'kitchens': kitchens.map((k) => k.toJson()).toList(),
        if (reportMeta != null) 'reportMeta': reportMeta!.toJson(),
      };
}
