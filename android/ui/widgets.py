# -*- coding: utf-8 -*-
"""
Piezas de interfaz reutilizables en toda la app: barra superior, tarjeta
con esquinas redondeadas, y una notificación tipo "snackbar". Se
construyen a mano con widgets de Kivy/KivyMD ya estables (sin usar
MDTopAppBar/MDDropdownMenu, cuya API cambió bastante en KivyMD 2.0) para
minimizar el riesgo de romperse entre versiones.
"""
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from . import theme as T


class RoundedCard(MDBoxLayout):
    """Contenedor con fondo blanco y esquinas redondeadas — el equivalente
    visual de las tarjetas (QGroupBox con esquinas redondeadas) de la
    versión de escritorio."""

    def __init__(self, bg_hex=T.CARD_BG, radius=14, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', dp(14))
        kwargs.setdefault('spacing', dp(8))
        kwargs.setdefault('size_hint_y', None)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        with self.canvas.before:
            self._color = Color(*T.hex_to_rgba(bg_hex))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._sync_rect, size=self._sync_rect)

    def _sync_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_bg(self, hex_color):
        self._color.rgba = T.hex_to_rgba(hex_color)


def top_bar(title, on_back=None, action_icon=None, on_action=None):
    """Barra superior simple: título, botón de regreso opcional y un botón
    de acción opcional (p.ej. "agregar")."""
    bar = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56),
                       padding=(dp(4), 0, dp(8), 0), md_bg_color=T.hex_to_rgba(T.PRIMARY))
    if on_back:
        back_btn = MDIconButton(icon='arrow-left', theme_icon_color='Custom', icon_color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda *_a: on_back())
        bar.add_widget(back_btn)
    else:
        bar.add_widget(MDBoxLayout(size_hint_x=None, width=dp(48)))
    lbl = MDLabel(text=title, theme_text_color='Custom', text_color=(1, 1, 1, 1),
                  font_style='Title', role='medium', valign='center')
    bar.add_widget(lbl)
    if action_icon:
        act_btn = MDIconButton(icon=action_icon, theme_icon_color='Custom', icon_color=(1, 1, 1, 1))
        if on_action:
            act_btn.bind(on_release=lambda *_a: on_action())
        bar.add_widget(act_btn)
    else:
        bar.add_widget(MDBoxLayout(size_hint_x=None, width=dp(48)))
    return bar


def filled_button(text, on_press, bg_hex=T.PRIMARY, icon=None):
    children = []
    if icon:
        children.append(MDButtonIcon(icon=icon, theme_icon_color='Custom', icon_color=(1, 1, 1, 1)))
    children.append(MDButtonText(text=text, theme_text_color='Custom', text_color=(1, 1, 1, 1)))
    btn = MDButton(*children, style='filled', md_bg_color=T.hex_to_rgba(bg_hex),
                   size_hint_y=None, height=dp(44))
    btn.bind(on_release=lambda *_a: on_press())
    return btn


def list_row(title, subtitle=None, on_open=None, on_delete=None, extra_actions=None):
    """Renglón de lista reutilizable (tarjeta blanca con título, subtítulo
    opcional, y botones de acción a la derecha) — se usa para Proyectos,
    Sistemas y Riesgos. extra_actions: lista opcional de (icono, callback)."""
    card = RoundedCard(size_hint_y=None)
    row = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing=dp(4))

    info = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(2))
    title_lbl = MDLabel(text=title, font_style='Title', role='small', adaptive_height=True,
                         theme_text_color='Custom', text_color=T.hex_to_rgba(T.TEXT))
    title_lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
    info.add_widget(title_lbl)
    if subtitle:
        sub_lbl = MDLabel(text=subtitle, adaptive_height=True, theme_text_color='Custom',
                           text_color=T.hex_to_rgba(T.MUTED), font_style='Label', role='large')
        sub_lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        info.add_widget(sub_lbl)
    row.add_widget(info)

    for icon, cb in (extra_actions or []):
        btn = MDIconButton(icon=icon)
        btn.bind(on_release=lambda *_a, _cb=cb: _cb())
        row.add_widget(btn)

    if on_open:
        open_btn = MDIconButton(icon='chevron-right')
        open_btn.bind(on_release=lambda *_a: on_open())
        row.add_widget(open_btn)
    if on_delete:
        del_btn = MDIconButton(icon='delete-outline', theme_icon_color='Custom', icon_color=T.hex_to_rgba(T.ERROR))
        del_btn.bind(on_release=lambda *_a: on_delete())
        row.add_widget(del_btn)

    card.add_widget(row)
    return card


def prompt_text(title, on_confirm, initial=''):
    """Modal sencillo con un campo de texto — para "Nuevo proyecto",
    "Nuevo sistema", "Renombrar", etc. Usa Popup (API estable de Kivy)
    en vez de MDDialog para evitar depender de la composición declarativa
    de KivyMD 2.0, que cambia con frecuencia entre versiones."""
    content = MDBoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16), size_hint_y=None, height=dp(160))
    field = MDTextField(MDTextFieldHintText(text='Nombre'), text=initial, mode='outlined',
                         size_hint_y=None, height=dp(56))
    content.add_widget(field)

    btn_row = MDBoxLayout(orientation='horizontal', spacing=dp(8), adaptive_height=True)
    popup = Popup(title=title, content=content, size_hint=(0.85, None), height=dp(220), auto_dismiss=False)

    def _confirm(*_a):
        text = field.text.strip()
        popup.dismiss()
        if text:
            on_confirm(text)

    cancel_btn = filled_button('Cancelar', popup.dismiss, bg_hex='#9e9e9e')
    ok_btn = filled_button('Aceptar', _confirm)
    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(ok_btn)
    content.add_widget(btn_row)

    popup.open()
    return popup


def confirm_dialog(title, message, on_confirm):
    """Modal de confirmación sí/no (para borrar proyectos/sistemas/riesgos)."""
    content = MDBoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16), size_hint_y=None, height=dp(140))
    content.add_widget(MDLabel(text=message, adaptive_height=True))
    btn_row = MDBoxLayout(orientation='horizontal', spacing=dp(8), adaptive_height=True)
    popup = Popup(title=title, content=content, size_hint=(0.85, None), height=dp(200), auto_dismiss=False)

    def _confirm(*_a):
        popup.dismiss()
        on_confirm()

    content.add_widget(btn_row)
    btn_row.add_widget(filled_button('Cancelar', popup.dismiss, bg_hex='#9e9e9e'))
    btn_row.add_widget(filled_button('Eliminar', _confirm, bg_hex=T.ERROR))
    popup.open()
    return popup


def show_snackbar(text):
    """Notificación breve en la parte inferior de la pantalla activa. Se
    construye a mano (un MDLabel dentro de una tarjeta oscura que se
    autodestruye) para no depender de la clase MDSnackbar de KivyMD 2.0,
    cuya composición declarativa cambia con frecuencia entre versiones.
    Se agrega a la pantalla actual (no al ScreenManager, que solo acepta
    widgets Screen) — cada Screen es un RelativeLayout, así que admite un
    hijo adicional posicionado con pos_hint superpuesto al contenido."""
    from kivymd.app import MDApp
    app = MDApp.get_running_app()
    if not app or not app.root or not app.root.current_screen:
        return
    screen = app.root.current_screen
    card = RoundedCard(bg_hex='#323232', radius=8, size_hint=(0.9, None), height=dp(44),
                        pos_hint={'center_x': 0.5, 'y': 0.03})
    card.add_widget(MDLabel(text=text, theme_text_color='Custom', text_color=(1, 1, 1, 1),
                             halign='center'))
    screen.add_widget(card)
    Clock.schedule_once(lambda *_a: screen.remove_widget(card) if card.parent else None, 2.2)
