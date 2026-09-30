import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:uuid/uuid.dart';

import '../calc/tank_selection.dart';
import '../models/catalog_entry.dart';
import '../models/equipment_item.dart';
import '../models/kitchen.dart';
import '../models/project.dart';
import '../services/storage_service.dart';

const _uuid = Uuid();
int _now() => DateTime.now().millisecondsSinceEpoch;

class KitchenSummary {
  final num totalFlow;
  final Map<String, int> nozzleTotals;
  final TankSelection tanks;
  final int itemCount;
  const KitchenSummary({required this.totalFlow, required this.nozzleTotals, required this.tanks, required this.itemCount});
}

class ProjectSummary {
  final Map<String, int> nozzleTotals;
  final num totalGallons;
  final int totalTanks;
  final List<({Kitchen kitchen, KitchenSummary summary})> kitchenSummaries;
  const ProjectSummary({required this.nozzleTotals, required this.totalGallons, required this.totalTanks, required this.kitchenSummaries});
}

/// Estado global de la app — equivalente al objeto `Store` de app.js (misma
/// forma de datos, mismas operaciones), pero como ChangeNotifier de Flutter
/// para poder re-renderizar la UI automáticamente en cada cambio.
class AppState extends ChangeNotifier {
  final StorageService _storage = StorageService();
  AppData _data = AppData.empty();
  List<CatalogEntry> _manualCatalog = [];
  bool _loading = true;

  AppData get data => _data;
  List<Project> get projects => _data.projects;
  bool get loading => _loading;

  Future<void> init() async {
    _manualCatalog = await _loadManualCatalog();
    _data = await _storage.load();
    _loading = false;
    notifyListeners();
  }

  Future<List<CatalogEntry>> _loadManualCatalog() async {
    final raw = await rootBundle.loadString('assets/model_catalog.json');
    final list = json.decode(raw) as List;
    return list.map((e) => CatalogEntry.fromJson(e as Map<String, dynamic>, source: 'manual')).toList();
  }

  Future<void> _persist() async {
    await _storage.save(_data);
  }

  Future<void> _mutate(void Function() fn) async {
    fn();
    notifyListeners();
    await _persist();
  }

  // --------------------------- Proyectos ----------------------------------
  Project? getProject(String id) {
    for (final p in _data.projects) {
      if (p.id == id) return p;
    }
    return null;
  }

  Kitchen? getKitchen(String pid, String kid) {
    final p = getProject(pid);
    if (p == null) return null;
    for (final k in p.kitchens) {
      if (k.id == kid) return k;
    }
    return null;
  }

  EquipmentItem? getEquipment(String pid, String kid, String eid) {
    final k = getKitchen(pid, kid);
    if (k == null) return null;
    for (final e in k.equipment) {
      if (e.id == eid) return e;
    }
    return null;
  }

  Future<Project> addProject(String name) async {
    final p = Project(id: _uuid.v4(), name: name.trim().isEmpty ? 'Proyecto sin nombre' : name.trim(), createdAt: _now());
    await _mutate(() => _data.projects.insert(0, p));
    return p;
  }

  Future<void> renameProject(String id, String name) async {
    await _mutate(() {
      _replaceProject(id, (p) => p.copyWith(name: name));
    });
  }

  Future<void> deleteProject(String id) async {
    await _mutate(() => _data.projects.removeWhere((p) => p.id == id));
  }

  void _replaceProject(String id, Project Function(Project) update) {
    final idx = _data.projects.indexWhere((p) => p.id == id);
    if (idx == -1) return;
    _data.projects[idx] = update(_data.projects[idx]);
  }

  // --------------------------- Cocinas --------------------------------------
  Future<Kitchen?> addKitchen(String pid, String name) async {
    final p = getProject(pid);
    if (p == null) return null;
    final k = Kitchen(id: _uuid.v4(), name: name.trim().isEmpty ? 'Cocina sin nombre' : name.trim(), createdAt: _now());
    await _mutate(() {
      _replaceProject(pid, (proj) => proj.copyWith(kitchens: [...proj.kitchens, k]));
    });
    return k;
  }

  Future<void> renameKitchen(String pid, String kid, String name) async {
    await _mutate(() {
      _replaceProject(pid, (p) => p.copyWith(kitchens: p.kitchens.map((k) => k.id == kid ? k.copyWith(name: name) : k).toList()));
    });
  }

  Future<void> deleteKitchen(String pid, String kid) async {
    await _mutate(() {
      _replaceProject(pid, (p) => p.copyWith(kitchens: p.kitchens.where((k) => k.id != kid).toList()));
    });
  }

  // --------------------------- Equipos ---------------------------------------
  Future<EquipmentItem?> addEquipment(String pid, String kid, EquipmentItem draft) async {
    final item = EquipmentItem(
      id: _uuid.v4(),
      category: draft.category,
      brand: draft.brand,
      model: draft.model,
      notes: draft.notes,
      input: draft.input,
      chosenIdx: draft.chosenIdx,
      catalogRef: draft.catalogRef,
      result: draft.result,
      createdAt: _now(),
    );
    await _mutate(() {
      _replaceProject(pid, (p) => p.copyWith(
            kitchens: p.kitchens.map((k) => k.id == kid ? k.copyWith(equipment: [...k.equipment, item]) : k).toList(),
          ));
    });
    return item;
  }

  Future<void> updateEquipment(String pid, String kid, String eid, EquipmentItem Function(EquipmentItem) update) async {
    await _mutate(() {
      _replaceProject(pid, (p) => p.copyWith(
            kitchens: p.kitchens.map((k) {
              if (k.id != kid) return k;
              return k.copyWith(equipment: k.equipment.map((e) => e.id == eid ? update(e) : e).toList());
            }).toList(),
          ));
    });
  }

  Future<void> deleteEquipment(String pid, String kid, String eid) async {
    await _mutate(() {
      _replaceProject(pid, (p) => p.copyWith(
            kitchens: p.kitchens.map((k) => k.id == kid ? k.copyWith(equipment: k.equipment.where((e) => e.id != eid).toList()) : k).toList(),
          ));
    });
  }

  // --------------------------- Catálogo de usuario ----------------------------
  CatalogEntry? getCatalogEntry(String id) {
    for (final e in _data.customCatalog) {
      if (e.id == id) return e;
    }
    return null;
  }

  Future<CatalogEntry> addCatalogEntry(CatalogEntry draft) async {
    final entry = draft.copyWith(id: _uuid.v4(), source: 'user', createdAt: _now());
    await _mutate(() => _data.customCatalog.add(entry));
    return entry;
  }

  Future<CatalogEntry?> updateCatalogEntry(String id, CatalogEntry Function(CatalogEntry) update) async {
    CatalogEntry? result;
    await _mutate(() {
      final idx = _data.customCatalog.indexWhere((e) => e.id == id);
      if (idx == -1) return;
      result = update(_data.customCatalog[idx]);
      _data.customCatalog[idx] = result!;
    });
    return result;
  }

  Future<void> deleteCatalogEntry(String id) async {
    await _mutate(() => _data.customCatalog.removeWhere((e) => e.id == id));
  }

  /// Combina el catálogo fijo del manual con el agregado por el usuario
  /// (el del usuario primero, igual que catalogEntriesForCategory en app2.js).
  List<CatalogEntry> catalogEntriesForCategory(String category) {
    final custom = _data.customCatalog.where((e) => e.category == category).toList();
    final manual = _manualCatalog.where((e) => e.category == category).toList();
    return [...custom, ...manual];
  }

  // --------------------------- Resúmenes (agregados) ---------------------------
  KitchenSummary kitchenSummary(Kitchen kitchen) {
    final nozzleTotals = <String, int>{};
    num totalFlow = 0;
    for (final item in kitchen.equipment) {
      final r = item.result;
      if (r == null) continue;
      totalFlow += r.flowNumber;
      for (final n in r.nozzles) {
        nozzleTotals[n.code] = (nozzleTotals[n.code] ?? 0) + n.qty;
      }
    }
    return KitchenSummary(totalFlow: totalFlow, nozzleTotals: nozzleTotals, tanks: selectTanks(totalFlow), itemCount: kitchen.equipment.length);
  }

  ProjectSummary projectSummary(Project project) {
    final nozzleTotals = <String, int>{};
    num totalGallons = 0;
    int totalTanks = 0;
    final kitchenSummaries = <({Kitchen kitchen, KitchenSummary summary})>[];
    for (final k in project.kitchens) {
      final s = kitchenSummary(k);
      kitchenSummaries.add((kitchen: k, summary: s));
      s.nozzleTotals.forEach((code, qty) => nozzleTotals[code] = (nozzleTotals[code] ?? 0) + qty);
      totalGallons += s.tanks.totalGallons;
      totalTanks += s.tanks.tankCount;
    }
    return ProjectSummary(nozzleTotals: nozzleTotals, totalGallons: totalGallons, totalTanks: totalTanks, kitchenSummaries: kitchenSummaries);
  }

  // --------------------------- Respaldo / restauración --------------------------
  Future<String> backupFilePath() => _storage.filePath();

  Future<void> exportBackupTo(String path) => _storage.exportTo(_data, path);

  /// Bytes del respaldo en JSON, listos para pasarle a file_picker (necesario
  /// en Android/iOS/Web, donde no hay una ruta de archivo escribible directa).
  Uint8List exportBackupBytes() => Uint8List.fromList(utf8.encode(json.encode(_data.toJson())));

  Future<void> restoreFrom(String path) async {
    final imported = await _storage.importFrom(path);
    await _mutate(() {
      _data = imported;
    });
  }

  String get lastResponsible => _data.lastResponsible;
  Future<void> setLastResponsible(String v) async {
    await _mutate(() => _data.lastResponsible = v);
  }
}
