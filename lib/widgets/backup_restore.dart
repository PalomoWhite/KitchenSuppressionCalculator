import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'app_scope.dart';

/// Respaldo/restauración manual — equivalente a los botones "Respaldar
/// datos"/"Restaurar" de la versión web (ahí exportaban/importaban un JSON;
/// aquí se hace lo mismo pero eligiendo la ruta con el selector nativo del
/// sistema — en Windows/macOS/Linux es una ruta de archivo real; en
/// Android/iOS/Web file_picker escribe el archivo él mismo a partir de los
/// bytes que le pasamos).
Future<void> exportBackupFlow(BuildContext context) async {
  final scope = AppScope.read(context);
  final bytes = scope.appState.exportBackupBytes();
  final path = await FilePicker.platform.saveFile(
    dialogTitle: 'Guardar respaldo de Ansul Flow Calculator',
    fileName: 'ansul_flow_calculator_respaldo.json',
    type: FileType.custom,
    allowedExtensions: ['json'],
    bytes: bytes,
  );
  if (path == null) return;
  if (!kIsWeb && (Platform.isWindows || Platform.isMacOS || Platform.isLinux)) {
    await File(path).writeAsBytes(bytes);
  }
  if (context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Respaldo guardado en $path')));
  }
}

Future<void> importBackupFlow(BuildContext context) async {
  final scope = AppScope.read(context);
  final result = await FilePicker.platform.pickFiles(
    dialogTitle: 'Elegir archivo de respaldo (.json)',
    type: FileType.custom,
    allowedExtensions: ['json'],
  );
  final path = result?.files.single.path;
  if (path == null) return;
  if (!context.mounted) return;
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Restaurar respaldo'),
      titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 14),
      contentPadding: const EdgeInsets.fromLTRB(24, 0, 24, 22),
      content: const Text('Esto reemplazará todos los proyectos y el catálogo actual en este dispositivo con los del archivo elegido. ¿Continuar?'),
      actions: [
        TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancelar')),
        FilledButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Restaurar')),
      ],
    ),
  );
  if (confirmed != true) return;
  await scope.appState.restoreFrom(path);
  if (context.mounted) {
    scope.navState.goHome();
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Datos restaurados correctamente.')));
  }
}
