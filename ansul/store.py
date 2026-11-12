# -*- coding: utf-8 -*-
"""
Almacenamiento local en JSON — equivalente al objeto Store (localStorage)
de AnsulCalc.html. Aquí la persistencia es un archivo en el disco del
usuario en vez del navegador, pero la forma de los datos y las operaciones
CRUD son las mismas: Proyectos -> Sistemas (antes "Cocinas") -> Riesgos
(antes "Equipos"), más un catálogo de equipos agregado por el usuario
(customCatalog). Los nombres internos (kitchen/equipment) se conservan en
el código y en el JSON guardado para no romper compatibilidad; solo cambió
la terminología mostrada al usuario.
"""
import json
import os
import random
import string
import time
from pathlib import Path

from . import data as D
from . import systems
from . import i18n

from .settings import APP_DIR_NAME, default_data_dir  # noqa: F401  (se re-exporta)
from .i18n import tr


def uid():
    letters = string.ascii_lowercase + string.digits
    return 'x' + ''.join(random.choice(letters) for _ in range(8)) + hex(int(time.time()))[-4:]


def today_iso():
    return time.strftime('%Y-%m-%d')


class Store:
    """Store con persistencia en un único archivo JSON."""

    def __init__(self, path=None):
        self.path = Path(path) if path else (default_data_dir() / 'ansulcalc_db.json')
        self.data = None
        self.corrupt_backup = None

    # ------------------------------ Carga / guardado -----------------------

    def load(self):
        self.corrupt_backup = None
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {'projects': [], 'lastResponsible': ''}
        except json.JSONDecodeError:
            self.data = {'projects': [], 'lastResponsible': ''}
            # El archivo dañado se aparta con un nombre nuevo, no se sobreescribe.
            sello = time.strftime('%Y%m%d-%H%M%S')
            respaldo = self.path.with_name(f'{self.path.stem}.corrupt-{sello}.json')
            os.replace(self.path, respaldo)
            self.corrupt_backup = respaldo
        except OSError:  # No se pudo leer el archivo: NO continuar con datos vacíos,
            raise        # el siguiente save() sobrescribirá el archivo.

        if 'projects' not in self.data:
            self.data['projects'] = []
        if 'customCatalog' not in self.data:
            self.data['customCatalog'] = []
        if 'lastResponsible' not in self.data:
            self.data['lastResponsible'] = ''

        migrated = False
        for p in self.data['projects']:
            # Proyectos anteriores a la versión con varias marcas: eran ANSUL.
            if not systems.is_valid(p.get('system')):
                p['system'] = systems.DEFAULT_SYSTEM
                migrated = True
            for k in p.get('kitchens', []):
                for item in k.get('equipment', []):
                    mapped = D.LEGACY_CATEGORY_MAP.get(item.get('category'))
                    if mapped:
                        item['category'] = mapped
                        migrated = True
        # Los textos de cada resultado (detalle, altura) se guardan en el idioma
        # en que se calcularon. Si el usuario cambió de idioma, se regeneran.
        if self.data.get('resultsLang', 'es') != i18n.language():
            self.regenerate_result_texts()
            self.data['resultsLang'] = i18n.language()
            migrated = True
        if migrated:
            self.save()
        return self.data

    @staticmethod
    def recompute_result(item, system):
        """Vuelve a calcular el resultado de un riesgo con sus medidas guardadas.
        Regresa None si no se puede (datos de catálogo, categoría o elección
        que ya no existen)."""
        if (item.get('catalogRef') or {}).get('hasFixedNozzles'):
            return None
        cdef = system.category_defs.get(item.get('category'))
        values = item.get('input') or {}
        if not cdef or not system.has_required_inputs(item['category'], values):
            return None
        try:
            calc = cdef['compute'](values)
            if cdef.get('has_choice'):
                matches = calc.get('matches') or []
                idx = item.get('chosenIdx', 0) or 0
                if not calc.get('ok') or not (0 <= idx < len(matches)):
                    return None
                return cdef['result_from_choice'](calc, idx)
            return calc.get('result') if calc.get('ok') else None
        except Exception:  # nunca romper la carga por un riesgo raro
            return None

    def regenerate_result_texts(self):
        """Regenera los textos de los resultados en el idioma activo. Solo
        reemplaza el resultado si las boquillas y el flow number salen
        IDÉNTICOS; si no, deja el resultado como estaba (no cambia cálculos)."""
        changed = 0
        for p in self.data.get('projects', []):
            system = systems.for_project(p)
            for k in p.get('kitchens', []):
                for item in k.get('equipment', []):
                    old = item.get('result')
                    new = self.recompute_result(item, system)
                    if not old or not new:
                        continue
                    if (new.get('nozzles') == old.get('nozzles')
                            and new.get('flowNumber') == old.get('flowNumber')):
                        item['result'] = new
                        changed += 1
        return changed

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.json.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    # ------------------------------ Catálogo de usuario ---------------------

    def get_catalog_entry(self, entry_id):
        return next((e for e in self.data.get('customCatalog', []) if e['id'] == entry_id), None)

    def add_catalog_entry(self, entry):
        entry = dict(entry)
        entry['id'] = uid()
        entry['createdAt'] = int(time.time() * 1000)
        self.data.setdefault('customCatalog', []).append(entry)
        self.save()
        return entry

    def update_catalog_entry(self, entry_id, patch):
        e = self.get_catalog_entry(entry_id)
        if not e:
            return None
        e.update(patch)
        self.save()
        return e

    def delete_catalog_entry(self, entry_id):
        self.data['customCatalog'] = [e for e in self.data.get('customCatalog', []) if e['id'] != entry_id]
        self.save()

    # ------------------------------ Proyectos / sistemas / riesgos -----------

    def get_project(self, pid):
        return next((p for p in self.data['projects'] if p['id'] == pid), None)

    def get_kitchen(self, pid, kid):
        p = self.get_project(pid)
        return p and next((k for k in p['kitchens'] if k['id'] == kid), None)

    def get_equipment(self, pid, kid, eid):
        k = self.get_kitchen(pid, kid)
        return k and next((e for e in k['equipment'] if e['id'] == eid), None)

    def add_project(self, name, system=None):
        system = system or systems.DEFAULT_SYSTEM
        if not systems.is_valid(system):
            raise ValueError(tr('Marca desconocida: {0}').format(system))
        p = {'id': uid(), 'name': name or tr('Proyecto sin nombre'), 'system': system,
             'createdAt': int(time.time() * 1000), 'kitchens': []}
        self.data['projects'].insert(0, p)
        self.save()
        return p

    def rename_project(self, pid, name):
        p = self.get_project(pid)
        if p:
            p['name'] = name
            self.save()

    @staticmethod
    def project_has_equipment(p):
        return any(k.get('equipment') for k in (p or {}).get('kitchens', []))

    def set_project_system(self, pid, system):
        """Cambia la marca del proyecto. Solo se permite si todavía no tiene
        riesgos (no hay proyectos mixtos — ver docs/DISEÑO.md)."""
        p = self.get_project(pid)
        if not p:
            return None
        if not systems.is_valid(system):
            raise ValueError(tr('Marca desconocida: {0}').format(system))
        if p.get('system') != system and self.project_has_equipment(p):
            raise ValueError(tr('No se puede cambiar la marca de un proyecto que ya tiene riesgos.'))
        p['system'] = system
        for k in p.get('kitchens', []):
            k.pop('tankOverride', None)
            k.pop('cylinderChoice', None)
        self.save()
        return p

    def delete_project(self, pid):
        self.data['projects'] = [p for p in self.data['projects'] if p['id'] != pid]
        self.save()

    def set_project_quote_number(self, pid, quote_number):
        p = self.get_project(pid)
        if p:
            p['quoteNumber'] = quote_number
            self.save()

    def add_kitchen(self, pid, name):
        p = self.get_project(pid)
        if not p:
            return None
        k = {'id': uid(), 'name': name or tr('Sistema sin nombre'),
             'createdAt': int(time.time() * 1000), 'equipment': []}
        p['kitchens'].append(k)
        self.save()
        return k

    def rename_kitchen(self, pid, kid, name):
        k = self.get_kitchen(pid, kid)
        if k:
            k['name'] = name
            self.save()

    def duplicate_kitchen(self, pid, kid):
        """Crea una copia del sistema (cocina) indicado dentro del mismo
        proyecto: mismo nombre + " (copia)", todos sus equipos/riesgos
        (con nuevos ids) y el override manual de tanques si lo tenía."""
        p = self.get_project(pid)
        k = self.get_kitchen(pid, kid)
        if not p or not k:
            return None
        new_kitchen = {
            'id': uid(),
            'name': tr('{0} (copia)').format(k['name']) if k.get('name') else '(copia)',
            'createdAt': int(time.time() * 1000),
            'equipment': [],
        }
        if k.get('tankOverride'):
            new_kitchen['tankOverride'] = dict(k['tankOverride'])
        if k.get('cylinderChoice'):
            new_kitchen['cylinderChoice'] = list(k['cylinderChoice'])
        p['kitchens'].append(new_kitchen)
        for item in k.get('equipment', []):
            copy = {k2: v for k2, v in item.items() if k2 not in ('id', 'createdAt')}
            copy['id'] = uid()
            copy['createdAt'] = int(time.time() * 1000)
            new_kitchen['equipment'].append(copy)
        self.save()
        return new_kitchen

    def delete_kitchen(self, pid, kid):
        p = self.get_project(pid)
        if p:
            p['kitchens'] = [k for k in p['kitchens'] if k['id'] != kid]
            self.save()

    def set_kitchen_tank_override(self, pid, kid, override):
        """override: None (usar selección automática) o
        {'enabled': bool, 'tanks': [3, 3, 1.5, ...]}."""
        k = self.get_kitchen(pid, kid)
        if k is not None:
            if override is None:
                k.pop('tankOverride', None)
            else:
                k['tankOverride'] = override
            self.save()

    def set_kitchen_cylinder_choice(self, pid, kid, cylinders):
        """Buckeye: combinación de cilindros elegida, p. ej. [10, 10, 5]
        (None = usar la primera opción de la lista)."""
        k = self.get_kitchen(pid, kid)
        if k is not None:
            if cylinders:
                k['cylinderChoice'] = sorted((int(c) for c in cylinders), reverse=True)
            else:
                k.pop('cylinderChoice', None)
            self.save()

    def add_equipment(self, pid, kid, item):
        k = self.get_kitchen(pid, kid)
        if not k:
            return None
        item = dict(item)
        item['id'] = uid()
        item['createdAt'] = int(time.time() * 1000)
        k['equipment'].append(item)
        self.save()
        return item

    def duplicate_equipment(self, pid, kid, eid):
        """Crea una copia del equipo/riesgo indicado dentro del mismo
        sistema (nuevo id/fecha, mismos datos capturados y resultado)."""
        item = self.get_equipment(pid, kid, eid)
        if not item:
            return None
        copy = {k2: v for k2, v in item.items() if k2 not in ('id', 'createdAt')}
        copy['model'] = tr('{0} (copia)').format(copy['model']) if copy.get('model') else '(copia)'
        return self.add_equipment(pid, kid, copy)

    def update_equipment(self, pid, kid, eid, patch):
        item = self.get_equipment(pid, kid, eid)
        if not item:
            return None
        item.update(patch)
        self.save()
        return item

    def delete_equipment(self, pid, kid, eid):
        k = self.get_kitchen(pid, kid)
        if k:
            k['equipment'] = [e for e in k['equipment'] if e['id'] != eid]
            self.save()

    # ------------------------------ Respaldo / restauración -----------------

    def export_backup(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def import_backup(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            incoming = json.load(f)
        if not isinstance(incoming, dict) or 'projects' not in incoming:
            raise ValueError(tr('El archivo no tiene el formato esperado de un respaldo de Ansul Flow Calculator.'))
        self.data = incoming
        for p in self.data['projects']:
            if not systems.is_valid(p.get('system')):
                p['system'] = systems.DEFAULT_SYSTEM
        if 'customCatalog' not in self.data:
            self.data['customCatalog'] = []
        if 'lastResponsible' not in self.data:
            self.data['lastResponsible'] = ''
        self.save()
