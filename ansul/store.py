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

APP_DIR_NAME = 'AnsulFlowCalculator'


def default_data_dir():
    """Carpeta de datos por defecto: Documentos/AnsulFlowCalculator (o el
    home del usuario si no existe una carpeta de Documentos estándar)."""
    home = Path.home()
    candidates = [home / 'Documents', home / 'Documentos']
    for c in candidates:
        if c.is_dir():
            return c / APP_DIR_NAME
    return home / APP_DIR_NAME


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

    # ------------------------------ Carga / guardado -----------------------

    def load(self):
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {'projects': [], 'lastResponsible': ''}
        except (json.JSONDecodeError, OSError):
            self.data = {'projects': [], 'lastResponsible': ''}

        if 'projects' not in self.data:
            self.data['projects'] = []
        if 'customCatalog' not in self.data:
            self.data['customCatalog'] = []
        if 'lastResponsible' not in self.data:
            self.data['lastResponsible'] = ''

        migrated = False
        for p in self.data['projects']:
            for k in p.get('kitchens', []):
                for item in k.get('equipment', []):
                    mapped = D.LEGACY_CATEGORY_MAP.get(item.get('category'))
                    if mapped:
                        item['category'] = mapped
                        migrated = True
        if migrated:
            self.save()
        return self.data

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

    def add_project(self, name):
        p = {'id': uid(), 'name': name or 'Proyecto sin nombre',
             'createdAt': int(time.time() * 1000), 'kitchens': []}
        self.data['projects'].insert(0, p)
        self.save()
        return p

    def rename_project(self, pid, name):
        p = self.get_project(pid)
        if p:
            p['name'] = name
            self.save()

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
        k = {'id': uid(), 'name': name or 'Sistema sin nombre',
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
            'name': f"{k['name']} (copia)" if k.get('name') else '(copia)',
            'createdAt': int(time.time() * 1000),
            'equipment': [],
        }
        if k.get('tankOverride'):
            new_kitchen['tankOverride'] = dict(k['tankOverride'])
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
        copy['model'] = f"{copy['model']} (copia)" if copy.get('model') else '(copia)'
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
            raise ValueError('El archivo no tiene el formato esperado de un respaldo de Ansul Flow Calculator.')
        self.data = incoming
        if 'customCatalog' not in self.data:
            self.data['customCatalog'] = []
        if 'lastResponsible' not in self.data:
            self.data['lastResponsible'] = ''
        self.save()
