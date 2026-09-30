import 'package:flutter/foundation.dart';

/// Una entrada de la pila de navegación — equivalente a los objetos que
/// app.js apila en `navStack` ({view, projectId, kitchenId, equipmentId}).
class NavEntry {
  final String view; // home | project | kitchen | equipmentForm | kitchenReport | projectReport | catalogManage
  final String? projectId;
  final String? kitchenId;
  final String? equipmentId;
  const NavEntry(this.view, {this.projectId, this.kitchenId, this.equipmentId});
}

/// Router simple de pila — puerto directo de navStack/nav/navReplace/
/// navBack/navHome en app.js, sin depender de paquetes externos de rutas.
class NavState extends ChangeNotifier {
  final List<NavEntry> _stack = [const NavEntry('home')];

  NavEntry get current => _stack.last;
  bool get canGoBack => _stack.length > 1;

  void push(NavEntry entry) {
    _stack.add(entry);
    notifyListeners();
  }

  void replace(NavEntry entry) {
    _stack[_stack.length - 1] = entry;
    notifyListeners();
  }

  void back() {
    if (_stack.length > 1) {
      _stack.removeLast();
      notifyListeners();
    }
  }

  /// Reinicia la pila a Inicio — usado por el título del panel lateral.
  void goHome() {
    _stack
      ..clear()
      ..add(const NavEntry('home'));
    notifyListeners();
  }
}
