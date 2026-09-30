# -*- coding: utf-8 -*-
"""
Formulario dinámico genérico construido a partir de las especificaciones
declarativas de ansul.category_defs (lista de dicts con 'key', 'type',
'label', etc.) — es el equivalente en Kivy/KivyMD de
ansul/ui/form_widgets.py (PySide6). Como category_defs.py describe los
campos de forma neutral a la interfaz, ESTE MISMO renderer cubre las 16
categorías de riesgo sin necesitar una pantalla distinta por categoría.
"""
from kivy.metrics import dp
from kivy.uix.spinner import Spinner
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.selectioncontrol import MDCheckbox

from . import theme as T


class DynamicForm(MDBoxLayout):
    """Señales (como callbacks en vez de Signal de Qt):
      on_changed()           -- cambió un campo "normal": basta recalcular.
      on_structure_changed() -- cambió un campo marcado con 'reflow': True
                                 (p.ej. "¿tiene escurridor?"): hay que
                                 reconstruir el formulario completo (puede
                                 cambiar qué campos se muestran) y luego
                                 recalcular.
    """

    def __init__(self, on_changed=None, on_structure_changed=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', dp(14))
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('padding', (0, dp(4), 0, dp(4)))
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.on_changed = on_changed
        self.on_structure_changed = on_structure_changed
        self._reflow_keys = set()
        self._values = {}

    def build(self, field_specs, values):
        """field_specs: lista de dicts (ver category_defs). values: dict
        mutable de valores actuales — se lee para precargar y se sigue
        usando como fuente de verdad tras cada edición."""
        self.clear_widgets()
        self._values = values
        self._reflow_keys = {spec['key'] for spec in field_specs if spec.get('reflow')}

        for spec in field_specs:
            key = spec['key']
            ftype = spec['type']
            label_text = spec.get('label', key)

            if ftype == 'info':
                lbl = MDLabel(text=label_text, theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED),
                               adaptive_height=True, halign='left')
                lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
                self.add_widget(lbl)
                continue

            required = spec.get('required', True)
            hint = spec.get('hint')
            full_label = label_text + (' *' if required and ftype != 'toggle' else '')

            if ftype == 'number':
                current = values.get(key, spec.get('default', ''))
                text_children = [MDTextFieldHintText(text=full_label)]
                if hint:
                    text_children.append(MDTextFieldHelperText(text=hint, mode='persistent'))
                tf = MDTextField(*text_children,
                                  text='' if current in (None, '') else str(current),
                                  input_filter='float', mode='outlined',
                                  size_hint_y=None, height=dp(72) if hint else dp(56))
                tf.bind(text=self._make_text_handler(key))
                self._values.setdefault(key, current if current not in (None, '') else None)
                self.add_widget(tf)

            elif ftype == 'select':
                options = spec.get('options', [])
                default = values.get(key, spec.get('default'))
                labels = [opt['label'] for opt in options]
                sel_label = next((opt['label'] for opt in options if str(opt['value']) == str(default)), (labels[0] if labels else ''))
                if default is not None and key not in values:
                    values[key] = default

                box = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(2))
                box.add_widget(MDLabel(text=full_label, adaptive_height=True, font_style='Label', role='large',
                                        theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED)))
                spinner = Spinner(text=sel_label, values=labels, size_hint=(1, None), height=dp(46),
                                   background_color=T.hex_to_rgba(T.PRIMARY_LIGHT), color=T.hex_to_rgba(T.TEXT))
                spinner.bind(text=self._make_select_handler(key, options))
                box.add_widget(spinner)
                if hint:
                    hint_lbl = MDLabel(text=hint, adaptive_height=True, font_style='Label', role='small',
                                        theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED))
                    box.add_widget(hint_lbl)
                self.add_widget(box)

            elif ftype == 'toggle':
                default = bool(values.get(key, spec.get('default', False)))
                if key not in values:
                    values[key] = default
                row = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing=dp(8))
                chk = MDCheckbox(active=default, size_hint=(None, None), size=(dp(36), dp(36)))
                chk.bind(active=self._make_toggle_handler(key))
                row.add_widget(chk)
                lbl = MDLabel(text=label_text, adaptive_height=True, valign='center')
                row.add_widget(lbl)
                self.add_widget(row)
                if hint:
                    hint_lbl = MDLabel(text=hint, adaptive_height=True, font_style='Label', role='small',
                                        theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED))
                    self.add_widget(hint_lbl)

    # ------------------------------------------------------------------
    def _make_text_handler(self, key):
        def handler(_instance, text):
            self._on_value_changed(key, text if text != '' else None)
        return handler

    def _make_select_handler(self, key, options):
        def handler(_instance, text):
            value = next((opt['value'] for opt in options if opt['label'] == text), None)
            self._on_value_changed(key, value)
        return handler

    def _make_toggle_handler(self, key):
        def handler(_instance, active):
            self._on_value_changed(key, bool(active))
        return handler

    def _on_value_changed(self, key, value):
        self._values[key] = value
        if key in self._reflow_keys:
            if self.on_structure_changed:
                self.on_structure_changed()
        else:
            if self.on_changed:
                self.on_changed()
