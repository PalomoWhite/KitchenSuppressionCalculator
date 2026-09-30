# -*- coding: utf-8 -*-
"""
Ansul Flow Calculator — versión Android (Kivy/KivyMD).

Punto de entrada de la app móvil. Reutiliza sin cambios el motor de
cálculo y la persistencia de la versión de escritorio (ansul/engine.py,
category_defs.py, data.py, store.py, report.py) — solo la interfaz está
reconstruida con Kivy/KivyMD, ver android/ui/.

Para desarrollo/pruebas en escritorio, basta con:
    python android/main.py

Para compilar el .apk, ver packaging/android/instalador_android.md.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Al compilar con buildozer, el paquete `ansul` se copia dentro de esta
# misma carpeta (android/ansul) por build_android.sh — de ahí que _HERE
# también se agregue al sys.path. En desarrollo normal (repo completo)
# `ansul` vive en la carpeta raíz del proyecto (_PARENT).
for _p in (_HERE, _PARENT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from ansul.store import Store

from ui.screens.projects_screen import ProjectsScreen
from ui.screens.systems_screen import SystemsScreen
from ui.screens.risks_screen import RisksScreen
from ui.screens.risk_form_screen import RiskFormScreen


class AnsulMobileApp(MDApp):
    title = 'Ansul Flow Calculator'

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'

        self.selected_project_id = None
        self.selected_kitchen_id = None

        self.store = Store(path=self._data_path())
        self.store.load()

        self.sm = MDScreenManager()
        self.projects_screen = ProjectsScreen(name='projects')
        self.systems_screen = SystemsScreen(name='systems')
        self.risks_screen = RisksScreen(name='risks')
        self.risk_form_screen = RiskFormScreen(name='risk_form')
        for screen in (self.projects_screen, self.systems_screen, self.risks_screen, self.risk_form_screen):
            self.sm.add_widget(screen)
        return self.sm

    def _data_path(self):
        """En Android, self.user_data_dir apunta al almacenamiento privado
        de la app (persiste entre actualizaciones, se borra si se
        desinstala — igual que cualquier app nativa). En escritorio (para
        pruebas) es una carpeta de configuración del usuario."""
        from pathlib import Path
        base = Path(self.user_data_dir)
        base.mkdir(parents=True, exist_ok=True)
        return base / 'ansulcalc_db.json'

    # ------------------------------------------------------------------
    # Navegación
    def go_projects(self):
        self.selected_project_id = None
        self.selected_kitchen_id = None
        self.sm.current = 'projects'

    def go_systems(self, project_id):
        self.selected_project_id = project_id
        self.selected_kitchen_id = None
        self.sm.current = 'systems'

    def go_risks(self, kitchen_id):
        self.selected_kitchen_id = kitchen_id
        self.sm.current = 'risks'

    def go_risk_form(self, equipment_id=None):
        self.risk_form_screen.load(equipment_id)
        self.sm.current = 'risk_form'


if __name__ == '__main__':
    AnsulMobileApp().run()
