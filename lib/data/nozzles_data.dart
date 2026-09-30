// Tabla 3-2: Nozzle Identification Chart (Sección 3, pág. 3-5) del manual
// ANSUL(R) R-102. Puerto directo de data.js -> NOZZLES.
class NozzleSpec {
  final String code;
  final num flow;
  final String partNo;
  const NozzleSpec({required this.code, required this.flow, required this.partNo});
}

const Map<String, NozzleSpec> kNozzles = {
  '1/2N': NozzleSpec(code: '1/2N', flow: 0.5, partNo: '443321'),
  '1F': NozzleSpec(code: '1F', flow: 1, partNo: '443319'),
  '1N': NozzleSpec(code: '1N', flow: 1, partNo: '443317'),
  '1W': NozzleSpec(code: '1W', flow: 1, partNo: '443323'),
  '2W': NozzleSpec(code: '2W', flow: 2, partNo: '443325'),
  '3N': NozzleSpec(code: '3N', flow: 3, partNo: '443327'),
  '230': NozzleSpec(code: '230', flow: 2, partNo: '443329'),
  '245': NozzleSpec(code: '245', flow: 2, partNo: '443331'),
  '260': NozzleSpec(code: '260', flow: 2, partNo: '443333'),
  '290': NozzleSpec(code: '290', flow: 2, partNo: '443335'),
  '2120': NozzleSpec(code: '2120', flow: 2, partNo: '443337'),
};

num nozzleFlow(String code) => kNozzles[code]?.flow ?? 0;
String nozzlePartNo(String code) => kNozzles[code]?.partNo ?? '—';
