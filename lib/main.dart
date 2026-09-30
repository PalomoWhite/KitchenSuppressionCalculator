import 'package:flutter/material.dart';
import 'state/app_state.dart';
import 'state/nav_state.dart';
import 'theme.dart';
import 'widgets/app_scope.dart';
import 'widgets/app_shell.dart';

void main() {
  runApp(const AnsulFlowApp());
}

class AnsulFlowApp extends StatefulWidget {
  const AnsulFlowApp({super.key});

  @override
  State<AnsulFlowApp> createState() => _AnsulFlowAppState();
}

class _AnsulFlowAppState extends State<AnsulFlowApp> {
  final AppState appState = AppState();
  final NavState navState = NavState();

  @override
  void initState() {
    super.initState();
    appState.init();
  }

  @override
  Widget build(BuildContext context) {
    return AppScope(
      appState: appState,
      navState: navState,
      child: MaterialApp(
        title: 'Ansul Flow Calculator',
        debugShowCheckedModeBanner: false,
        theme: buildAppTheme(brightness: Brightness.light),
        darkTheme: buildAppTheme(brightness: Brightness.dark),
        themeMode: ThemeMode.system,
        home: const AppShell(),
      ),
    );
  }
}
