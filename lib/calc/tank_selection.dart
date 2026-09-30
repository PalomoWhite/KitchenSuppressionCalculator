// Selección de tanques y cartuchos — puerto directo de calc.js -> selectTanks().
// Basado en Tank and Cartridge Requirements (pág. 4-77) y System Selection
// Guide (pág. 9-1 a 9-4): cada tanque de 3 gal aporta 11 "flow numbers" de
// capacidad y cada tanque de 1.5 gal aporta 5. Números de parte de cartucho
// verificados contra ambas tablas del manual R-102 (Rev. 13, 2022-NOV-14).
const String kN2Lt20r = 'LT-20-R (No. 423429)';
const String kN2Lt30r = 'LT-30-R (No. 423435)';
const String kN2Double = 'Doble / Double (No. 423493)';
const String kCo2_101_10 = '101-10 (No. 423439)';
const String kCo2_101_20 = '101-20 (No. 423441)';
const String kCo2_101_30 = '101-30 (No. 423443)';
const String kMultiCartridgeNote =
    'Sistema de 3 o más tanques: se arma con un ensamble de liberación regulada (1 tanque) más actuador(es) regulado(s) adicionales (hasta 3 tanques c/u). El cartucho de la liberación es LT-20-R (1.5 gal) o LT-30-R (3 gal); cada actuador usa cartucho Doble (No. 423493) o LT-A-101-30 (No. 423491) según si los tanques van "manifolded". Existen varias combinaciones válidas — verifique la combinación exacta para su configuración en la Guía de Selección de Sistema (Sección 9, pág. 9-1 a 9-4) del manual R-102.';

class TankSelection {
  final int tankCount;
  final List<num> tanks;
  final num totalGallons;
  final String? n2;
  final String? co2;
  final String? note;
  const TankSelection({required this.tankCount, required this.tanks, required this.totalGallons, this.n2, this.co2, this.note});
}

TankSelection selectTanks(num totalFlow) {
  if (totalFlow <= 0) {
    return const TankSelection(tankCount: 0, tanks: [], totalGallons: 0);
  }
  if (totalFlow <= 5) {
    return const TankSelection(tankCount: 1, tanks: [1.5], totalGallons: 1.5, n2: kN2Lt20r, co2: kCo2_101_10);
  }
  if (totalFlow <= 11) {
    return const TankSelection(tankCount: 1, tanks: [3], totalGallons: 3, n2: kN2Lt30r, co2: kCo2_101_20);
  }
  // n >= 2 tanques: probar combinación de (n-1) tanques de 3 gal + 1 de 1.5
  // gal, luego n tanques de 3 gal — se elige la de menor capacidad que alcance.
  for (var n = 2; n <= 20; n++) {
    final capA = 11 * (n - 1) + 5;
    final capB = 11 * n;
    if (totalFlow <= capA) {
      // growable: true es obligatorio aquí — List.filled() por default crea una
      // lista de tamaño fijo, y el ..add(1.5) de abajo tronaría con
      // "Cannot add to a fixed-length list" en cuanto un cálculo cayera en
      // esta rama (n-1 tanques de 3 gal + 1 de 1.5 gal).
      final tanks = List<num>.filled(n - 1, 3, growable: true)..add(1.5);
      return TankSelection(
        tankCount: n,
        tanks: tanks,
        totalGallons: 3 * (n - 1) + 1.5,
        n2: n == 2 ? kN2Double : 'Ver nota',
        co2: n == 2 ? kCo2_101_30 : 'Ver nota',
        note: n >= 3 ? kMultiCartridgeNote : null,
      );
    }
    if (totalFlow <= capB) {
      final tanks = List<num>.filled(n, 3);
      return TankSelection(
        tankCount: n,
        tanks: tanks,
        totalGallons: 3 * n,
        n2: n == 2 ? kN2Double : 'Ver nota',
        co2: n == 2 ? kCo2_101_30 : 'Ver nota',
        note: n >= 3 ? kMultiCartridgeNote : null,
      );
    }
  }
  return const TankSelection(tankCount: 0, tanks: [], totalGallons: 0, note: 'Flow number excede el máximo tabulado (>220). Requiere diseño especializado — consulte a ANSUL.');
}
