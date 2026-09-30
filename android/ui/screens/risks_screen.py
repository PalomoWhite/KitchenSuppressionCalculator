# -*- coding: utf-8 -*-
"""Pantalla "Riesgos" — los equipos/riesgos capturados dentro de un
sistema, con el resumen de tanques/flow number y el botón de generar PDF
(equivalente a la tabla "Riesgos, ductos y plenos" de la ventana
principal de escritorio)."""
import os
import time

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel

from ansul import engine as E
from ansul import report as R
from ansul.category_defs import category_display_label, dimensions_display, depth_display

from .. import theme as T
from ..widgets import top_bar, list_row, filled_button, RoundedCard, confirm_dialog, show_snackbar


class RisksScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = T.hex_to_rgba(T.SCREEN_BG)
        self.root_box = MDBoxLayout(orientation='vertical')
        self.scroll = MDScrollView()
        self.content_box = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12), size_hint_y=None)
        self.content_box.bind(minimum_height=self.content_box.setter('height'))
        self.scroll.add_widget(self.content_box)
        self.add_widget(self.root_box)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        kitchen = app.store.get_kitchen(app.selected_project_id, app.selected_kitchen_id)
        self.root_box.clear_widgets()
        if not kitchen:
            app.go_systems(app.selected_project_id)
            return
        self.root_box.add_widget(top_bar(kitchen['name'], on_back=lambda: app.go_systems(app.selected_project_id),
                                          action_icon='plus', on_action=lambda: app.go_risk_form(None)))
        self.root_box.add_widget(self.scroll)

        self.content_box.clear_widgets()
        summary = E.kitchen_summary(kitchen)
        self.content_box.add_widget(self._build_summary_card(summary))

        equipment = kitchen.get('equipment', [])
        if not equipment:
            self.content_box.add_widget(MDLabel(
                text='Este sistema todavía no tiene riesgos.\nToca + arriba para agregar el primero.',
                halign='center', adaptive_height=True, theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED)))
            return

        for item in equipment:
            self.content_box.add_widget(self._build_risk_row(item))

    def _build_summary_card(self, summary):
        card = RoundedCard(bg_hex=T.PRIMARY_LIGHT)
        card.add_widget(MDLabel(text='Resumen del sistema', font_style='Title', role='small', adaptive_height=True,
                                 theme_text_color='Custom', text_color=T.hex_to_rgba(T.PRIMARY)))
        tanks = summary['tanks']
        tank_txt = (f"{tanks.get('tankCount', 0)} tanque(s) — {', '.join(f'{t} gal' for t in tanks.get('tanks', []))}"
                    if tanks.get('tankCount') else 'Sin riesgos calculados todavía')
        card.add_widget(MDLabel(text=f"Flow number total: {E.fmt_num(summary['totalFlow'])}", adaptive_height=True))
        card.add_widget(MDLabel(text=f"Tanques: {tank_txt}", adaptive_height=True))
        if tanks.get('note'):
            card.add_widget(MDLabel(text=tanks['note'], adaptive_height=True, theme_text_color='Custom',
                                     text_color=T.hex_to_rgba(T.MUTED), font_style='Label', role='small'))
        card.add_widget(filled_button('Generar reporte PDF de este sistema', self._generate_pdf, icon='file-pdf-box'))
        return card

    def _build_risk_row(self, item):
        app = MDApp.get_running_app()
        label = category_display_label(item)
        dims = dimensions_display(item) or '—'
        depth = depth_display(item)
        result = item.get('result') or {}
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (result.get('nozzles') or [])) or 'Sin boquillas'
        flow_txt = E.fmt_num(result.get('flowNumber'))
        parts = [f"{dims}"]
        if depth:
            parts.append(f"Prof. {depth}")
        parts.append(f"Boquillas: {nozz_txt}")
        parts.append(f"Flow: {flow_txt}")
        subtitle = ' · '.join(parts)
        brand_model = ' '.join(x for x in (item.get('brand'), item.get('model')) if x)
        title = f"{label}" + (f" — {brand_model}" if brand_model else '')

        return list_row(
            title, subtitle,
            on_open=lambda eid=item['id']: app.go_risk_form(eid),
            on_delete=lambda eid=item['id'], t=title: self._confirm_delete(eid, t),
            extra_actions=[('content-copy', lambda eid=item['id']: self._duplicate(eid))],
        )

    def _duplicate(self, eid):
        app = MDApp.get_running_app()
        app.store.duplicate_equipment(app.selected_project_id, app.selected_kitchen_id, eid)
        self.refresh()
        show_snackbar('Riesgo duplicado')

    def _confirm_delete(self, eid, title):
        def do_delete():
            app = MDApp.get_running_app()
            app.store.delete_equipment(app.selected_project_id, app.selected_kitchen_id, eid)
            self.refresh()
            show_snackbar(f'"{title}" eliminado')
        confirm_dialog('Eliminar riesgo', f'¿Eliminar "{title}" de este sistema?', do_delete)

    def _generate_pdf(self):
        app = MDApp.get_running_app()
        project = app.store.get_project(app.selected_project_id)
        kitchen = app.store.get_kitchen(app.selected_project_id, app.selected_kitchen_id)
        if not project or not kitchen:
            return
        reports_dir = os.path.join(app.user_data_dir, 'reportes')
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"{R.pdf_sanitize_filename(kitchen['name'])}_{time.strftime('%Y%m%d_%H%M')}.pdf"
        out_path = os.path.join(reports_dir, filename)
        try:
            R.build_kitchen_report_pdf(project, kitchen, out_path,
                                        quote_number=project.get('quoteNumber', ''))
        except Exception as exc:  # noqa: BLE001 — mostrar cualquier error al usuario, no solo los esperados
            show_snackbar(f'No se pudo generar el PDF: {exc}')
            return
        self._share_or_notify(out_path)

    @staticmethod
    def _share_or_notify(path):
        try:
            from plyer import share
            share.share(filepath=path, title='Compartir reporte PDF')
        except Exception:
            show_snackbar(f'PDF guardado en almacenamiento de la app: {os.path.basename(path)}')
