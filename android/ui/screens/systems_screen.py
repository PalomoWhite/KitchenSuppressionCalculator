# -*- coding: utf-8 -*-
"""Pantalla "Sistemas" — los sistemas (antes "cocinas") de un proyecto."""
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel

from ansul import engine as E

from .. import theme as T
from ..widgets import top_bar, list_row, prompt_text, confirm_dialog, show_snackbar


class SystemsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = T.hex_to_rgba(T.SCREEN_BG)
        root = MDBoxLayout(orientation='vertical')
        self.bar_title = MDLabel()  # placeholder, replaced by top_bar each refresh
        self.root_box = root
        self.scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.scroll.add_widget(self.list_box)
        self.add_widget(root)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        project = app.store.get_project(app.selected_project_id)
        self.root_box.clear_widgets()
        if not project:
            app.go_projects()
            return
        self.root_box.add_widget(top_bar(project['name'], on_back=app.go_projects,
                                          action_icon='plus', on_action=self._new_system))
        self.root_box.add_widget(self.scroll)

        self.list_box.clear_widgets()
        kitchens = project.get('kitchens', [])
        if not kitchens:
            self.list_box.add_widget(MDLabel(
                text='Este proyecto todavía no tiene sistemas.\nToca + arriba para agregar el primero.',
                halign='center', adaptive_height=True, theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED)))
            return
        for k in kitchens:
            s = E.kitchen_summary(k)
            n_riesgos = len(k.get('equipment', []))
            subtitle = f"{n_riesgos} riesgo(s) · flow number {E.fmt_num(s['totalFlow'])} · {s['tanks'].get('tankCount', 0)} tanque(s)"
            row = list_row(
                k['name'], subtitle,
                on_open=lambda kid=k['id']: app.go_risks(kid),
                on_delete=lambda kid=k['id'], name=k['name']: self._confirm_delete(kid, name),
                extra_actions=[('content-copy', lambda kid=k['id']: self._duplicate(kid))],
            )
            self.list_box.add_widget(row)

    def _new_system(self):
        def on_confirm(name):
            app = MDApp.get_running_app()
            app.store.add_kitchen(app.selected_project_id, name)
            self.refresh()
            show_snackbar(f'Sistema "{name}" creado')
        prompt_text('Nuevo sistema', on_confirm)

    def _duplicate(self, kid):
        app = MDApp.get_running_app()
        app.store.duplicate_kitchen(app.selected_project_id, kid)
        self.refresh()
        show_snackbar('Sistema duplicado')

    def _confirm_delete(self, kid, name):
        def do_delete():
            app = MDApp.get_running_app()
            app.store.delete_kitchen(app.selected_project_id, kid)
            self.refresh()
            show_snackbar(f'Sistema "{name}" eliminado')
        confirm_dialog('Eliminar sistema',
                        f'¿Eliminar el sistema "{name}" y todos sus riesgos? Esta acción no se puede deshacer.',
                        do_delete)
