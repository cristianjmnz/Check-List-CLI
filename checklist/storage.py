"""Persistencia en SQLite: lectura/escritura atómica y backup ante corrupción.

Los datos viven en un único archivo `tareas.db`. Si no existe y hay archivos
JSON legacy (`tareas.json`, `tags.json`, `config.json`) en el mismo directorio,
se importan automáticamente la primera vez. Los JSON nunca se modifican.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style

from . import models, paths

# Códigos de error de SQLite que indican un archivo realmente corrupto
# (SQLITE_CORRUPT y SQLITE_NOTADB). Un bloqueo (SQLITE_BUSY/SQLITE_LOCKED) no lo es.
_CODIGOS_CORRUPCION = {11, 26}
_MENSAJES_CORRUPCION = (
    "file is not a database",
    "database disk image is malformed",
    "malformed database",
)


def _es_corrupcion(exc):
    """True solo si el error indica un archivo corrupto, no un bloqueo temporal."""
    if getattr(exc, "sqlite_errorcode", None) in _CODIGOS_CORRUPCION:
        return True
    mensaje = str(exc).lower()
    return any(fragmento in mensaje for fragmento in _MENSAJES_CORRUPCION)


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


# ─── Conexión, esquema y migración ───────────────────────────────────────────


def _conectar(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _crear_esquema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            completada INTEGER NOT NULL DEFAULT 0,
            fecha TEXT,
            tag TEXT,
            prioridad TEXT NOT NULL DEFAULT 'media'
        )
        """
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tags (nombre TEXT PRIMARY KEY, color TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS config (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)"
    )
    conn.commit()


def _migrar_desde_json(db_path):
    """Importa los JSON legacy del mismo directorio (idempotente)."""
    db = Path(db_path)
    conn = _conectar(db)
    try:
        _crear_esquema(conn)

        data, estado = _leer_json(db.parent / "tareas.json")
        if estado == "ok" and isinstance(data, list):
            for t in data:
                tarea = models.normalizar_tarea(t)
                if tarea is not None:
                    conn.execute(
                        "INSERT INTO tareas (texto, completada, fecha, tag, prioridad) "
                        "VALUES (?,?,?,?,?)",
                        (
                            tarea["texto"],
                            int(bool(tarea["completada"])),
                            tarea.get("fecha"),
                            tarea.get("tag"),
                            tarea.get("prioridad", "media"),
                        ),
                    )

        data, estado = _leer_json(db.parent / "tags.json")
        if estado == "ok" and isinstance(data, dict):
            for nombre, color in models.normalizar_tags(
                data, paths.COLORES_DISPONIBLES
            ).items():
                conn.execute(
                    "INSERT OR REPLACE INTO tags (nombre, color) VALUES (?,?)",
                    (nombre, color),
                )

        data, estado = _leer_json(db.parent / "config.json")
        if estado == "ok" and isinstance(data, dict):
            for clave, valor in models.normalizar_config(data).items():
                conn.execute(
                    "INSERT OR REPLACE INTO config (clave, valor) VALUES (?,?)",
                    (clave, str(valor)),
                )

        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def _abrir_db(db_path):
    """Garantiza que la base existe (migrando JSON si hace falta) y su esquema."""
    db = Path(db_path)
    if not db.exists():
        _migrar_desde_json(db)
    conn = _conectar(db)
    try:
        _crear_esquema(conn)
    except sqlite3.Error:
        conn.close()
        raise
    return conn


# ─── Acceso con recuperación ante corrupción ────────────────────────────────


def _ejecutar_lectura(db_path, consulta):
    conn = _abrir_db(db_path)
    try:
        return conn.execute(consulta).fetchall()
    finally:
        conn.close()


def _leer(db_path, consulta):
    """Ejecuta `consulta` y devuelve las filas. Ante corrupción respalda el archivo
    y reintenta sobre una base nueva; los bloqueos y errores transitorios se propagan."""
    try:
        return _ejecutar_lectura(db_path, consulta)
    except sqlite3.Error as exc:
        if not _es_corrupcion(exc):
            raise
        _respaldar_corrupto(db_path, "Base de datos corrupta")
        return _ejecutar_lectura(db_path, consulta)


def _ejecutar_escritura(db_path, operacion):
    conn = _abrir_db(db_path)
    try:
        conn.execute("BEGIN")
        operacion(conn)
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def _escribir(db_path, operacion):
    """Ejecuta `operacion(conn)` en una transacción. Ante corrupción respalda el
    archivo y reintenta sobre una base nueva; los bloqueos se propagan."""
    try:
        _ejecutar_escritura(db_path, operacion)
    except sqlite3.Error as exc:
        if not _es_corrupcion(exc):
            raise
        _respaldar_corrupto(db_path, "Base de datos corrupta")
        _ejecutar_escritura(db_path, operacion)


# ─── Tareas ──────────────────────────────────────────────────────────────────


def cargar_tareas(db_path=None):
    db_path = paths.DB if db_path is None else Path(db_path)
    filas = _leer(
        db_path,
        "SELECT id, texto, completada, fecha, tag, prioridad FROM tareas ORDER BY id",
    )
    return [t for t in (models.normalizar_tarea(dict(r)) for r in filas) if t is not None]


def guardar_tareas(tareas, db_path=None):
    """Hace upsert por id (INSERT/UPDATE/DELETE) en una transacción."""
    db_path = paths.DB if db_path is None else Path(db_path)

    def operacion(conn):
        ids_db = {r["id"] for r in conn.execute("SELECT id FROM tareas")}
        ids_in = set()
        for t in tareas:
            normalizada = models.normalizar_tarea(t)
            if normalizada is None:
                continue
            tid = normalizada.get("id")
            valores = (
                normalizada["texto"],
                int(bool(normalizada["completada"])),
                normalizada.get("fecha"),
                normalizada.get("tag"),
                normalizada.get("prioridad", "media"),
            )
            if tid is None or tid not in ids_db:
                cur = conn.execute(
                    "INSERT INTO tareas (texto, completada, fecha, tag, prioridad) "
                    "VALUES (?,?,?,?,?)",
                    valores,
                )
                t["id"] = cur.lastrowid
            else:
                ids_in.add(tid)
                conn.execute(
                    "UPDATE tareas SET texto=?, completada=?, fecha=?, tag=?, "
                    "prioridad=? WHERE id=?",
                    valores + (tid,),
                )
        for tid in ids_db - ids_in:
            conn.execute("DELETE FROM tareas WHERE id=?", (tid,))

    _escribir(db_path, operacion)


# ─── Tags ────────────────────────────────────────────────────────────────────


def cargar_tags(db_path=None):
    db_path = paths.DB if db_path is None else Path(db_path)
    filas = _leer(db_path, "SELECT nombre, color FROM tags")
    return models.normalizar_tags(
        {r["nombre"]: r["color"] for r in filas}, paths.COLORES_DISPONIBLES
    )


def guardar_tags(tags, db_path=None):
    db_path = paths.DB if db_path is None else Path(db_path)

    def operacion(conn):
        conn.execute("DELETE FROM tags")
        for nombre, color in tags.items():
            conn.execute(
                "INSERT OR REPLACE INTO tags (nombre, color) VALUES (?,?)",
                (nombre, color),
            )

    _escribir(db_path, operacion)


# ─── Configuración ───────────────────────────────────────────────────────────


def cargar_config(db_path=None):
    db_path = paths.DB if db_path is None else Path(db_path)
    filas = _leer(db_path, "SELECT clave, valor FROM config")
    return models.normalizar_config({r["clave"]: r["valor"] for r in filas})


def guardar_config(config, db_path=None):
    db_path = paths.DB if db_path is None else Path(db_path)

    def operacion(conn):
        conn.execute("DELETE FROM config")
        for clave, valor in config.items():
            conn.execute(
                "INSERT OR REPLACE INTO config (clave, valor) VALUES (?,?)",
                (clave, str(valor)),
            )

    _escribir(db_path, operacion)
