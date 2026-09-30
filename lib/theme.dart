import 'package:flutter/material.dart';

// Mismo azul de marca que la versión web (--brand: #0554a3 / --accent: #0968c4),
// ahora como semilla de un esquema de color Material 3 completo.
const kBrandBlue = Color(0xFF0554A3);
const kBrandBlueDark = Color(0xFF033E7A);
const kAccentBlue = Color(0xFF0968C4);
const kDanger = Color(0xFFC0392B);
const kOk = Color(0xFF1E8E5A);
const kWarn = Color(0xFFB8860B);

ThemeData buildAppTheme({required Brightness brightness}) {
  final scheme = ColorScheme.fromSeed(
    seedColor: kBrandBlue,
    brightness: brightness,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: brightness == Brightness.dark ? const Color(0xFF0E1116) : const Color(0xFFF3F6FA),
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: kBrandBlue,
      selectedIconTheme: const IconThemeData(color: Colors.white),
      unselectedIconTheme: IconThemeData(color: Colors.white.withOpacity(0.75)),
      selectedLabelTextStyle: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700),
      unselectedLabelTextStyle: TextStyle(color: Colors.white.withOpacity(0.85)),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: scheme.surface,
      foregroundColor: scheme.onSurface,
      elevation: 0,
      scrolledUnderElevation: 1,
      centerTitle: false,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: kBrandBlue,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    ),
    cardTheme: CardThemeData(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: scheme.outlineVariant)),
      margin: EdgeInsets.zero,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surfaceContainerHighest.withOpacity(0.35),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
      // Padding superior más grande que el inferior: cuando la etiqueta flota
      // arriba (con valor ya elegido, como "Combustible: Gas") necesita ese
      // aire extra o se ve pegada al borde de la caja.
      contentPadding: const EdgeInsets.fromLTRB(14, 20, 14, 14),
    ),
    dividerTheme: DividerThemeData(color: scheme.outlineVariant),
    // Nota: DialogThemeData NO tiene 'titlePadding' ni 'contentPadding' (esos
    // solo existen directo en cada widget AlertDialog, no a nivel de tema) —
    // por eso el espaciado extra del contenido se puso en cada AlertDialog
    // individualmente en vez de aquí. Aquí solo van las propiedades que sí
    // son válidas a nivel de tema global.
    dialogTheme: DialogThemeData(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      actionsPadding: const EdgeInsets.fromLTRB(24, 0, 24, 20),
    ),
  );
}
