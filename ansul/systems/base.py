# -*- coding: utf-8 -*-
"""
SystemDef — lo que toda marca (ANSUL, Buckeye, …) le ofrece a la interfaz y
al reporte PDF. Ver docs/DISEÑO.md, sección 3.
"""
from ..i18n import tr


class SystemDef:
    key = ''
    label = ''              # Nombre completo que ve el usuario
    short = ''              # Nombre corto (árbol de proyectos)
    flow_label = tr('Flow number')
    report_subtitle = ''
    disclaimer = ''
    disclaimer_short = ''

    supports_catalog = False
    supports_tank_override = False
    supports_cylinder_choice = False

    # Categorías
    category_order = ()
    category_labels = {}
    category_defs = {}

    def has_required_inputs(self, category, values):
        raise NotImplementedError

    def category_display_label(self, item):
        return self.category_labels.get(item.get('category'), item.get('category'))

    def dimensions_display(self, item):
        return None

    def depth_display(self, item):
        return None

    def diagram_spec(self, category, values):
        """None = usar el diagrama propio del widget (solo ANSUL)."""
        return None

    # Boquillas
    def nozzle_columns(self):
        return [tr('Boquilla'), tr('No. de parte'), tr('Cantidad')]

    def nozzle_row(self, code, qty):
        return [code, '—', str(qty)]

    # Resúmenes
    def kitchen_summary(self, kitchen):
        raise NotImplementedError

    def project_summary(self, project):
        raise NotImplementedError

    def summary_rows(self, summary):
        """[(concepto, cantidad), …] del resumen de materiales de un sistema."""
        raise NotImplementedError

    def summary_notes(self, summary):
        """Textos de aviso (lista) para mostrar debajo del resumen."""
        return []

    def containers_short(self, summary):
        """Texto corto de tanques/cilindros para la tabla de sistemas."""
        return '—'

    def project_rows(self, project_summary):
        raise NotImplementedError
