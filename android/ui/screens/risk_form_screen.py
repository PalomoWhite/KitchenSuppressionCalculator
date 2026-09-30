# -*- coding: utf-8 -*-
"""Pantalla "Agregar/editar riesgo" — construye el formulario dinámico
según la categoría elegida y muestra en vivo el resultado (boquillas /
flow number), igual que ansul/ui/equipment_dialog.py en la versión de
escritorio, pero con widgets de Kivy/KivyMD."""
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from ansul import data as D
from ansul import engine as E
from ansul import category_defs as CD

from .. import theme as T
from ..dynamic_form import DynamicForm
from ..widgets import top_bar, filled_button, RoundedCard, show_snackbar


class _ChoiceRow(ButtonBehavior, RoundedCard):
    pass


class RiskFormScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = T.hex_to_rgba(T.SCREEN_BG)

        self.existing_item = None
        self.category = 'fryer'
        self.values = {}
        self.chosen_idx = 0
        self.current_calc = None
        self.final_result = None

        self.root_box = MDBoxLayout(orientation='vertical')
        self.scroll = MDScrollView()
        self.content_box = MDBoxLayout(orientation='vertical', spacing=dp(14), padding=dp(14), size_hint_y=None)
        self.content_box.bind(minimum_height=self.content_box.setter('height'))
        self.scroll.add_widget(self.content_box)
        self.add_widget(self.root_box)

        # --- Piezas fijas (categoría, marca/modelo, notas) ---
        self.category_spinner = Spinner(text=D.CATEGORY_LABELS[self.category],
                                         values=[D.CATEGORY_LABELS[k] for k in D.CATEGORY_ORDER],
                                         size_hint_y=None, height=dp(46),
                                         background_color=T.hex_to_rgba(T.PRIMARY_LIGHT), color=T.hex_to_rgba(T.TEXT))
        self.category_spinner.bind(text=self._on_category_label_changed)

        self.brand_field = MDTextField(MDTextFieldHintText(text='Marca (opcional)'), mode='outlined',
                                        size_hint_y=None, height=dp(56))
        self.model_field = MDTextField(MDTextFieldHintText(text='Modelo (opcional)'), mode='outlined',
                                        size_hint_y=None, height=dp(56))
        self.notes_field = MDTextField(MDTextFieldHintText(text='Notas (opcional)'), mode='outlined',
                                        size_hint_y=None, height=dp(56))

        self.form = DynamicForm(on_changed=self._recompute, on_structure_changed=self._on_structure_changed)

        self.choice_box = MDBoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=(0, dp(4)))
        self.choice_box.bind(minimum_height=self.choice_box.setter('height'))
        self.choice_label = MDLabel(text='Opciones de boquilla disponibles — elige una', font_style='Title',
                                     role='small', adaptive_height=True, theme_text_color='Custom',
                                     text_color=T.hex_to_rgba(T.PRIMARY))

        self.result_card = RoundedCard()
        self.result_label = MDLabel(text='Complete los datos para calcular la boquilla requerida.',
                                     adaptive_height=True)
        self.result_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        self.result_card.add_widget(self.result_label)

        self.save_btn = filled_button('Guardar riesgo', self._on_save, icon='content-save')

    # ------------------------------------------------------------------
    def load(self, equipment_id):
        app = MDApp.get_running_app()
        self.existing_item = None
        if equipment_id:
            self.existing_item = app.store.get_equipment(app.selected_project_id, app.selected_kitchen_id, equipment_id)

        item = self.existing_item or {}
        self.category = item.get('category', 'fryer')
        self.values = dict(item.get('input') or {})
        self.chosen_idx = item.get('chosenIdx') or 0
        self.current_calc = None
        self.final_result = None

        self.category_spinner.text = D.CATEGORY_LABELS[self.category]
        self.brand_field.text = item.get('brand', '')
        self.model_field.text = item.get('model', '')
        self.notes_field.text = item.get('notes', '')

        self._layout_screen('Editar riesgo' if self.existing_item else 'Agregar riesgo')
        self._rebuild_form()
        self._recompute()

    def _layout_screen(self, title):
        app = MDApp.get_running_app()
        self.root_box.clear_widgets()
        self.root_box.add_widget(top_bar(title, on_back=lambda: app.go_risks(app.selected_kitchen_id)))
        self.root_box.add_widget(self.scroll)

        self.content_box.clear_widgets()
        self.content_box.add_widget(MDLabel(text='Categoría de riesgo', adaptive_height=True, font_style='Label',
                                             role='large', theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED)))
        self.content_box.add_widget(self.category_spinner)
        self.content_box.add_widget(self.brand_field)
        self.content_box.add_widget(self.model_field)
        self.content_box.add_widget(self.notes_field)
        self.content_box.add_widget(self.form)
        self.content_box.add_widget(self.choice_box)
        self.content_box.add_widget(self.result_card)
        self.content_box.add_widget(self.save_btn)

    # ------------------------------------------------------------------
    def _on_category_label_changed(self, _instance, label_text):
        new_cat = next((k for k in D.CATEGORY_ORDER if D.CATEGORY_LABELS[k] == label_text), self.category)
        if new_cat == self.category:
            return
        self.category = new_cat
        self.values = {}
        self.chosen_idx = 0
        self._rebuild_form()
        self._recompute()

    def _rebuild_form(self):
        cdef = CD.CATEGORY_DEFS[self.category]
        specs = cdef['fields'](self.values)
        self.form.build(specs, self.values)

    def _on_structure_changed(self):
        self._rebuild_form()
        self._recompute()

    # ------------------------------------------------------------------
    def _recompute(self):
        cdef = CD.CATEGORY_DEFS[self.category]

        if not CD.has_required_inputs(self.category, self.values):
            self.choice_box.clear_widgets()
            self.final_result = None
            self._set_result_style(None)
            self.result_label.text = 'Complete los datos requeridos (*) para calcular la boquilla.'
            return

        calc = cdef['compute'](self.values)
        self.current_calc = calc

        if cdef.get('has_choice'):
            matches = calc.get('matches') or []
            if not calc.get('ok') or not matches:
                self.choice_box.clear_widgets()
                self.final_result = None
                self._show_error(cdef['not_fit_msg'](self.values, calc))
                return
            self._build_choice_list(cdef, matches)
            idx = self.chosen_idx if 0 <= self.chosen_idx < len(matches) else 0
            self.chosen_idx = idx
            self.final_result = cdef['result_from_choice'](calc, idx)
            self._show_result(self.final_result)
        else:
            self.choice_box.clear_widgets()
            if not calc.get('ok'):
                self.final_result = None
                self._show_error(cdef['not_fit_msg'](self.values, calc))
                return
            self.final_result = calc.get('result')
            self._show_result(self.final_result)

    def _build_choice_list(self, cdef, matches):
        self.choice_box.clear_widgets()
        self.choice_box.add_widget(self.choice_label)
        for i, m in enumerate(matches):
            label = cdef['choice_label'](m)
            sub = cdef['choice_sub'](m)
            selected = (i == self.chosen_idx)
            row = _ChoiceRow(bg_hex=(T.PRIMARY_LIGHT if selected else T.CARD_BG), size_hint_y=None)
            title_lbl = MDLabel(text=label, adaptive_height=True, theme_text_color='Custom',
                                 text_color=T.hex_to_rgba(T.PRIMARY if selected else T.TEXT))
            sub_lbl = MDLabel(text=sub, adaptive_height=True, font_style='Label', role='small',
                               theme_text_color='Custom', text_color=T.hex_to_rgba(T.MUTED))
            for lbl in (title_lbl, sub_lbl):
                lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            row.add_widget(title_lbl)
            row.add_widget(sub_lbl)
            row.bind(on_release=lambda _inst, idx=i: self._choice_selected(idx))
            self.choice_box.add_widget(row)

    def _choice_selected(self, idx):
        if not self.current_calc:
            return
        self.chosen_idx = idx
        cdef = CD.CATEGORY_DEFS[self.category]
        matches = self.current_calc.get('matches') or []
        self._build_choice_list(cdef, matches)
        self.final_result = cdef['result_from_choice'](self.current_calc, idx)
        self._show_result(self.final_result)

    # ------------------------------------------------------------------
    def _show_result(self, result):
        if not result:
            self._show_error('No se pudo calcular un resultado.')
            return
        nozz_txt = ', '.join(f"{n['code']} ×{n['qty']}" for n in (result.get('nozzles') or [])) or 'Sin boquillas (informativo)'
        text = (f"Boquillas: {nozz_txt}\nFlow number: {E.fmt_num(result.get('flowNumber'))}\n"
                f"Altura de montaje: {result.get('heightRange', '—')}\nDetalle: {result.get('detail', '')}")
        self.result_label.text = text
        self._set_result_style('ok')

    def _show_error(self, msg):
        self.result_label.text = msg or 'Estas medidas no encajan en ninguna opción estándar del manual R-102.'
        self._set_result_style('error')

    def _set_result_style(self, kind):
        if kind == 'ok':
            self.result_card.set_bg(T.OK_BG)
            self.result_label.theme_text_color = 'Custom'
            self.result_label.text_color = T.hex_to_rgba('#1e5c22')
        elif kind == 'error':
            self.result_card.set_bg(T.ERROR_BG)
            self.result_label.theme_text_color = 'Custom'
            self.result_label.text_color = T.hex_to_rgba(T.ERROR)
        else:
            self.result_card.set_bg(T.CARD_BG)
            self.result_label.theme_text_color = 'Custom'
            self.result_label.text_color = T.hex_to_rgba(T.MUTED)

    # ------------------------------------------------------------------
    def _on_save(self):
        if not self.final_result:
            show_snackbar('Complete los datos necesarios para obtener un resultado válido antes de guardar.')
            return
        app = MDApp.get_running_app()
        item = {
            'category': self.category,
            'brand': self.brand_field.text.strip(),
            'model': self.model_field.text.strip(),
            'notes': self.notes_field.text.strip(),
            'input': dict(self.values),
            'chosenIdx': self.chosen_idx,
            'catalogRef': (self.existing_item or {}).get('catalogRef'),
            'result': self.final_result,
        }
        if self.existing_item:
            app.store.update_equipment(app.selected_project_id, app.selected_kitchen_id,
                                        self.existing_item['id'], item)
        else:
            app.store.add_equipment(app.selected_project_id, app.selected_kitchen_id, item)
        app.go_risks(app.selected_kitchen_id)
        show_snackbar('Riesgo guardado')
