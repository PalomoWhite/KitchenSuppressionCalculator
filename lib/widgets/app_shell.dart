import 'package:flutter/material.dart';
import '../screens/catalog_manage_screen.dart';
import '../screens/equipment_form_screen.dart';
import '../screens/home_screen.dart';
import '../screens/kitchen_report_screen.dart';
import '../screens/kitchen_screen.dart';
import '../screens/project_report_screen.dart';
import '../screens/project_screen.dart';
import '../state/nav_state.dart';
import 'app_scope.dart';
import 'backup_restore.dart';

/// Estructura general de la app: panel lateral persistente (equivalente al
/// panel de escritorio "Opción B" de la versión web) + área de contenido que
/// cambia según la pila de navegación (NavState).
class AppShell extends StatelessWidget {
  const AppShell({super.key});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    return Scaffold(
      body: ListenableBuilder(
        listenable: Listenable.merge([scope.appState, scope.navState]),
        builder: (context, _) {
          if (scope.appState.loading) {
            return const Center(child: CircularProgressIndicator());
          }
          return Row(
            children: [
              _Sidebar(width: 280),
              const VerticalDivider(width: 1),
              Expanded(child: _Content(entry: scope.navState.current)),
            ],
          );
        },
      ),
    );
  }
}

class _Content extends StatelessWidget {
  final NavEntry entry;
  const _Content({required this.entry});

  @override
  Widget build(BuildContext context) {
    switch (entry.view) {
      case 'project':
        return ProjectScreen(projectId: entry.projectId!);
      case 'kitchen':
        return KitchenScreen(projectId: entry.projectId!, kitchenId: entry.kitchenId!);
      case 'equipmentForm':
        return EquipmentFormScreen(projectId: entry.projectId!, kitchenId: entry.kitchenId!, equipmentId: entry.equipmentId);
      case 'kitchenReport':
        return KitchenReportScreen(projectId: entry.projectId!, kitchenId: entry.kitchenId!);
      case 'projectReport':
        return ProjectReportScreen(projectId: entry.projectId!);
      case 'catalogManage':
        return const CatalogManageScreen();
      case 'home':
      default:
        return const HomeScreen();
    }
  }
}

class _Sidebar extends StatelessWidget {
  final double width;
  const _Sidebar({required this.width});

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final nav = scope.navState;
    final app = scope.appState;
    final activeProjectId = nav.current.projectId;
    final activeKitchenId = nav.current.kitchenId;

    return Container(
      width: width,
      color: const Color(0xFF0554A3),
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextButton(
              onPressed: () => nav.goHome(),
              style: TextButton.styleFrom(
                alignment: Alignment.center,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.fromLTRB(18, 26, 18, 20),
              ),
              child: const Text(
                'Ansul Flow Calculator',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
            ),
            const SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: FilledButton.tonal(
                onPressed: () => _newProject(context),
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.white.withOpacity(0.14),
                  foregroundColor: Colors.white,
                  alignment: Alignment.centerLeft,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
                ),
                child: const Text('+ Nuevo proyecto'),
              ),
            ),
            const SizedBox(height: 18),
            Expanded(
              child: app.projects.isEmpty
                  ? const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 18),
                      child: Text('Aún no tienes proyectos', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    )
                  : ListView(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      children: app.projects.map((p) {
                        final isActive = p.id == activeProjectId;
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            InkWell(
                              borderRadius: BorderRadius.circular(8),
                              onTap: () => nav.push(NavEntry('project', projectId: p.id)),
                              hoverColor: Colors.white.withOpacity(0.10),
                              splashColor: Colors.white.withOpacity(0.16),
                              highlightColor: Colors.white.withOpacity(0.10),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                                decoration: BoxDecoration(
                                  color: isActive ? Colors.white.withOpacity(0.16) : null,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    Icon(isActive ? Icons.expand_more : Icons.chevron_right, size: 16, color: Colors.white),
                                    const SizedBox(width: 6),
                                    Expanded(
                                      child: Text(p.name,
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            if (isActive) const SizedBox(height: 6),
                            if (isActive)
                              if (p.kitchens.isEmpty)
                                const Padding(
                                  padding: EdgeInsets.fromLTRB(30, 6, 10, 6),
                                  child: Text('Sin cocinas', style: TextStyle(color: Colors.white60, fontSize: 12.5)),
                                )
                              else
                                ...p.kitchens.map((k) {
                                  final kActive = k.id == activeKitchenId;
                                  return InkWell(
                                    borderRadius: BorderRadius.circular(8),
                                    onTap: () => nav.push(NavEntry('kitchen', projectId: p.id, kitchenId: k.id)),
                                    hoverColor: kActive ? Colors.black.withOpacity(0.04) : Colors.white.withOpacity(0.10),
                                    splashColor: kActive ? Colors.black.withOpacity(0.08) : Colors.white.withOpacity(0.16),
                                    highlightColor: kActive ? Colors.black.withOpacity(0.04) : Colors.white.withOpacity(0.10),
                                    child: Container(
                                      margin: const EdgeInsets.only(bottom: 5),
                                      padding: const EdgeInsets.fromLTRB(30, 10, 10, 10),
                                      decoration: BoxDecoration(
                                        color: kActive ? Colors.white : null,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(
                                        k.name,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          color: kActive ? const Color(0xFF033E7A) : Colors.white.withOpacity(0.88),
                                          fontWeight: kActive ? FontWeight.w700 : FontWeight.w500,
                                          fontSize: 13.5,
                                        ),
                                      ),
                                    ),
                                  );
                                }),
                            const SizedBox(height: 6),
                          ],
                        );
                      }).toList(),
                    ),
            ),
            const Divider(color: Colors.white24, height: 18),
            _FooterLink(label: 'Catálogo de equipos (tus modelos)', onTap: () => nav.push(const NavEntry('catalogManage'))),
            _FooterLink(label: 'Respaldar datos', onTap: () => exportBackupFlow(context)),
            _FooterLink(label: 'Restaurar', onTap: () => importBackupFlow(context)),
            const SizedBox(height: 14),
          ],
        ),
      ),
    );
  }

  void _newProject(BuildContext context) {
    final scope = AppScope.read(context);
    showDialog<void>(
      context: context,
      builder: (ctx) => _NamePromptDialog(
        title: 'Nuevo proyecto',
        label: 'Nombre del proyecto',
        onSave: (name) async {
          final p = await scope.appState.addProject(name);
          scope.navState.push(NavEntry('project', projectId: p.id));
        },
      ),
    );
  }
}

class _FooterLink extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _FooterLink({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    // InkWell ya trae hover/splash por default, pero su color por default es
    // oscuro y prácticamente invisible sobre el azul del sidebar — por eso no
    // se sentía como que "iluminaba" al pasar el mouse. Se especifican colores
    // claros explícitos (y un margen/radio para que se vea como botón).
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          hoverColor: Colors.white.withOpacity(0.12),
          splashColor: Colors.white.withOpacity(0.18),
          highlightColor: Colors.white.withOpacity(0.10),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 11),
            child: Text(label, style: const TextStyle(color: Colors.white70, fontSize: 12.5)),
          ),
        ),
      ),
    );
  }
}

/// Diálogo reutilizable para pedir un nombre (nuevo proyecto/cocina, o
/// renombrar) — equivalente a promptModal() en app.js.
class _NamePromptDialog extends StatefulWidget {
  final String title;
  final String label;
  final String initialValue;
  final Future<void> Function(String) onSave;
  const _NamePromptDialog({required this.title, required this.label, this.initialValue = '', required this.onSave});

  @override
  State<_NamePromptDialog> createState() => _NamePromptDialogState();
}

class _NamePromptDialogState extends State<_NamePromptDialog> {
  late final TextEditingController _controller = TextEditingController(text: widget.initialValue);

  void _submit() {
    final v = _controller.text.trim();
    if (v.isEmpty) return;
    Navigator.of(context).pop();
    widget.onSave(v);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.title),
      titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 14),
      contentPadding: const EdgeInsets.fromLTRB(24, 0, 24, 22),
      content: TextField(
        controller: _controller,
        autofocus: true,
        decoration: InputDecoration(labelText: widget.label),
        onSubmitted: (_) => _submit(),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancelar')),
        FilledButton(onPressed: _submit, child: const Text('Guardar')),
      ],
    );
  }
}

/// Diálogo de confirmación reutilizable — equivalente a confirmModal() en app.js.
Future<bool> confirmDialog(BuildContext context, {required String title, required String message, String confirmLabel = 'Eliminar'}) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(title),
      titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 14),
      contentPadding: const EdgeInsets.fromLTRB(24, 0, 24, 22),
      content: Text(message),
      actions: [
        TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancelar')),
        FilledButton(
          style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
          onPressed: () => Navigator.of(ctx).pop(true),
          child: Text(confirmLabel),
        ),
      ],
    ),
  );
  return result ?? false;
}

Future<void> promptDialog(
  BuildContext context, {
  required String title,
  required String label,
  String initialValue = '',
  required Future<void> Function(String) onSave,
}) {
  return showDialog<void>(
    context: context,
    builder: (ctx) => _NamePromptDialog(title: title, label: label, initialValue: initialValue, onSave: onSave),
  );
}
