"""Persistencia en JSON: lectura/escritura atómica y backup ante corrupción."""

import json
import os
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style

from . import models, paths


def _leer_json(path):
    """Devuelve (data, estado) con estado en {'ok', 'missing', 'corrupt'}."""
    path = Path(path)
    if not path.exists():
        return None, "missing"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), "ok"
    except (json.JSONDecodeError, UnicodeError, OSError):
        return None, "corrupt"


def _respaldar_corrupto(path, etiqueta):
    try:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = str(path) + f".corrupt-{ts}"
        os.replace(path, backup)
        print(
            Fore.RED
            + f"  {etiqueta}. Se respaldó como {backup}"
            + Style.RESET_ALL
        )
    except Exception:
        pass


def _guardar_json(path, data):
    tmp = str(path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, path)


def cargar_tareas(path=None):
    path = path or paths.FILE
    data, estado = _leer_json(path)
    if estado == "missing":
        return []
    if estado == "corrupt":
        _respaldar_corrupto(path, "Archivo corrupto")
        return []
    if not isinstance(data, list):
        _respaldar_corrupto(path, "Archivo corrupto (formato inesperado)")
        return []
    return [t for t in (models.normalizar_tarea(x) for x in data) if t is not None]


def guardar_tareas(tareas, path=None):
    _guardar_json(path or paths.FILE, tareas)


def cargar_tags(path=None):
    path = path or paths.FILE_TAGS
    data, estado = _leer_json(path)
    if estado == "missing":
        return {}
    if estado == "corrupt":
        _respaldar_corrupto(path, "Archivo tags corrupto")
        return {}
    if not isinstance(data, dict):
        _respaldar_corrupto(path, "Archivo tags corrupto (formato inesperado)")
        return {}
    return models.normalizar_tags(data, paths.COLORES_DISPONIBLES)


def guardar_tags(tags, path=None):
    _guardar_json(path or paths.FILE_TAGS, tags)


def cargar_config(path=None):
    path = path or paths.FILE_CONFIG
    data, estado = _leer_json(path)
    if estado in ("missing", "corrupt"):
        if estado == "corrupt":
            _respaldar_corrupto(path, "Config corrupta")
        return {}
    return models.normalizar_config(data)


def guardar_config(config, path=None):
    _guardar_json(path or paths.FILE_CONFIG, config)
