import 'package:flutter/material.dart';
import '../state/app_state.dart';
import '../state/nav_state.dart';

/// Provee AppState/NavState a todo el árbol de widgets sin depender de un
/// paquete externo de manejo de estado — un InheritedWidget simple.
class AppScope extends InheritedWidget {
  final AppState appState;
  final NavState navState;

  const AppScope({super.key, required this.appState, required this.navState, required super.child});

  /// Uso normal dentro de build(): se suscribe a cambios (rebuild cuando el
  /// AppScope se reemplaza — en la práctica AppState/NavState son
  /// ChangeNotifier y se escuchan aparte con ListenableBuilder).
  static AppScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppScope>();
    assert(scope != null, 'AppScope.of() llamado sin un AppScope en el árbol.');
    return scope!;
  }

  /// Lectura sin suscripción — segura de llamar en initState(), callbacks de
  /// botones, etc. (no intenta registrar una dependencia de build).
  static AppScope read(BuildContext context) {
    final scope = context.findAncestorWidgetOfExactType<AppScope>();
    assert(scope != null, 'AppScope.read() llamado sin un AppScope en el árbol.');
    return scope!;
  }

  @override
  bool updateShouldNotify(AppScope oldWidget) => appState != oldWidget.appState || navState != oldWidget.navState;
}
