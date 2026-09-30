import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../models/project.dart';
import '../models/catalog_entry.dart';

/// Persistencia local en un archivo JSON — equivalente de escritorio al
/// localStorage de la versión web (misma forma de datos: { projects,
/// customCatalog, lastResponsible }), guardado en la carpeta de datos de la
/// app en el dispositivo del usuario (no en la nube).
class AppData {
  List<Project> projects;
  List<CatalogEntry> customCatalog; // source siempre 'user'
  String lastResponsible;

  AppData({required this.projects, required this.customCatalog, this.lastResponsible = ''});

  factory AppData.empty() => AppData(projects: [], customCatalog: []);

  factory AppData.fromJson(Map<String, dynamic> j) {
    final projects = ((j['projects'] as List?) ?? []).map((e) => Project.fromJson(e as Map<String, dynamic>)).toList();
    final customCatalog = ((j['customCatalog'] as List?) ?? [])
        .map((e) => CatalogEntry.fromJson(e as Map<String, dynamic>, source: 'user'))
        .toList();
    final data = AppData(projects: projects, customCatalog: customCatalog, lastResponsible: (j['lastResponsible'] as String?) ?? '');
    _migrateLegacyCategories(data);
    return data;
  }

  // Puerto de la migración LEGACY_CATEGORY_MAP en app.js -> Store.load():
  // renglones guardados con una clave de categoría antigua se remapean a la
  // vigente para que no fallen al mostrarse/editarse.
  static void _migrateLegacyCategories(AppData data) {
    for (final p in data.projects) {
      for (final k in p.kitchens) {
        for (var i = 0; i < k.equipment.length; i++) {
          final item = k.equipment[i];
          final mapped = kLegacyCategoryMap[item.category];
          if (mapped != null) {
            k.equipment[i] = item.copyWith(category: mapped);
          }
        }
      }
    }
  }

  Map<String, dynamic> toJson() => {
        'projects': projects.map((p) => p.toJson()).toList(),
        'customCatalog': customCatalog.map((c) => c.toJson()).toList(),
        'lastResponsible': lastResponsible,
      };
}

class StorageService {
  static const _fileName = 'ansulcalc_db_v1.json';
  File? _file;

  Future<File> _getFile() async {
    if (_file != null) return _file!;
    final dir = await getApplicationSupportDirectory();
    if (!await dir.exists()) await dir.create(recursive: true);
    _file = File('${dir.path}${Platform.pathSeparator}$_fileName');
    return _file!;
  }

  Future<String> filePath() async => (await _getFile()).path;

  Future<AppData> load() async {
    try {
      final file = await _getFile();
      if (!await file.exists()) return AppData.empty();
      final raw = await file.readAsString();
      if (raw.trim().isEmpty) return AppData.empty();
      final j = json.decode(raw) as Map<String, dynamic>;
      return AppData.fromJson(j);
    } catch (_) {
      return AppData.empty();
    }
  }

  Future<void> save(AppData data) async {
    final file = await _getFile();
    await file.writeAsString(json.encode(data.toJson()));
  }

  /// Exporta un respaldo a una ruta elegida por el usuario (mismo formato
  /// que el archivo de datos, portable entre dispositivos).
  Future<void> exportTo(AppData data, String path) async {
    final file = File(path);
    await file.writeAsString(json.encode(data.toJson()));
  }

  Future<AppData> importFrom(String path) async {
    final file = File(path);
    final raw = await file.readAsString();
    final j = json.decode(raw) as Map<String, dynamic>;
    return AppData.fromJson(j);
  }
}
