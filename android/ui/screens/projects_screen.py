# -*- coding: utf-8 -*-
"""Pantalla "Proyectos" — la raíz de la navegación (equivalente al panel
izquierdo de la ventana principal de escritorio)."""
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel

from .. import theme as T
from ..widgets import top_bar, list_row, prompt_text, confirm_dialog, show_snackbar


class ProjectsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = T.hex_to_rgba(T.SCREEN_BG)
        root = MDBoxLayout(orientation='vertical')
        root.add_widget(top_bar('Ansul Flow Calculator', action_icon='plus', on_action=self._new_project))

        self.scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)
        self.add_widget(root)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        self.list_box.clear_widgets()
        projects = app.store.data['projects']
        if not projects:
            self.list_box.add_widget(MDLabel(
                text='No hay proyectos todavía.\nToca + arriba para crear el primero.',
                halign='center', adaptive_height=True, theme_text_color='Custom',
                text_color=T.hex_to_rgba(T.MUTED)))
            return
        for p in projects:
            n_sistemas = len(p.get('kitchens', []))
            subtitle = f"{n_sistemas} sistema(s) · creado {self._fmt_date(p.get('createdAt'))}"
            row = list_row(
                p['name'], subtitle,
                on_open=lambda pid=p['id']: app.go_systems(pid),
                on_delete=lambda pid=p['id'], name=p['name']: self._confirm_delete(pid, name),
            )
            self.list_box.add_widget(row)

    @staticmethod
    def _fmt_date(ms):
        if not ms:
            return '—'
        import time
        return time.strftime('%Y-%m-%d', time.localtime(ms / 1000))

    def _new_project(self):
        def on_confirm(name):
            app = MDApp.get_running_app()
            app.store.add_project(name)
            self.refresh()
            show_snackbar(f'Proyecto "{name}" creado')
        prompt_text('Nuevo proyecto', on_confirm)

    def _confirm_delete(self, pid, name):
        def do_delete():
            app = MDApp.get_running_app()
            app.store.delete_project(pid)
            self.refresh()
            show_snackbar(f'Proyecto "{name}" eliminado')
        confirm_dialog('Eliminar proyecto',
                        f'¿Eliminar el proyecto "{name}" y todos sus sistemas y riesgos? Esta acción no se puede deshacer.',
                        do_delete)
