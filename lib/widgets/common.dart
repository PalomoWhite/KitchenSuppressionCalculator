import 'package:flutter/material.dart';
import '../theme.dart';

String fmtNum(num? n) {
  if (n == null || n.isNaN) return '—';
  final r = (n * 100).round() / 100;
  if (r == r.roundToDouble()) return r.toInt().toString();
  var s = r.toString();
  if (s.contains('.')) {
    s = s.replaceFirst(RegExp(r'0+$'), '');
    s = s.replaceFirst(RegExp(r'\.$'), '');
  }
  return s;
}

String fmtDate(int? epochMs) {
  if (epochMs == null) return '';
  final d = DateTime.fromMillisecondsSinceEpoch(epochMs);
  const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  return '${d.day} ${months[d.month - 1]} ${d.year}';
}

enum BannerKind { info, ok, warn }

class AppBanner extends StatelessWidget {
  final String text;
  final BannerKind kind;
  final Widget? trailing;
  const AppBanner(this.text, {super.key, this.kind = BannerKind.info, this.trailing});

  @override
  Widget build(BuildContext context) {
    final Color bg;
    final Color fg;
    switch (kind) {
      case BannerKind.ok:
        bg = kOk.withOpacity(0.12);
        fg = kOk;
        break;
      case BannerKind.warn:
        bg = kWarn.withOpacity(0.14);
        fg = kWarn;
        break;
      case BannerKind.info:
        bg = kAccentBlue.withOpacity(0.10);
        fg = kBrandBlueDark;
        break;
    }
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(10)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(text, style: TextStyle(color: fg, fontSize: 13.5, height: 1.5)),
          if (trailing != null) Padding(padding: const EdgeInsets.only(top: 10), child: trailing),
        ],
      ),
    );
  }
}

class SectionTitle extends StatelessWidget {
  final String text;
  const SectionTitle(this.text, {super.key});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: 22, bottom: 11),
        child: Text(text, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700, letterSpacing: 0.4, color: Colors.black54)),
      );
}

class ListItemCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  const ListItemCard({super.key, required this.title, required this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14.5)),
                    const SizedBox(height: 5),
                    Text(subtitle, style: TextStyle(color: Colors.grey.shade600, fontSize: 12.5)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.black38),
            ],
          ),
        ),
      ),
    );
  }
}

class EmptyState extends StatelessWidget {
  final String text;
  const EmptyState(this.text, {super.key});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 28),
        child: Center(child: Text(text, textAlign: TextAlign.center, style: TextStyle(color: Colors.grey.shade600))),
      );
}

class TopBarAction extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  const TopBarAction({super.key, required this.label, required this.onPressed});
  @override
  Widget build(BuildContext context) => TextButton(onPressed: onPressed, child: Text(label));
}
