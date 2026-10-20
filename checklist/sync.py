"""Aplica al CLI las tareas completadas desde los botones de ntfy."""

import hmac
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

from colorama import Fore, Style

from . import paths, storage

_CMD_RE = re.compile(r"^done:(\d+):([A-Za-z0-9_-]+)$")
_TIMEOUT = 5


def _parse_comando(texto):
    coincidencia = _CMD_RE.match((texto or "").strip())
    if not coincidencia:
        return None
    return int(coincidencia.group(1)), coincidencia.group(2)


def _leer_mensajes(server, cmd_topic, since):
    url = (
        f"{server.rstrip('/')}/{cmd_topic}/json"
        f"?poll=1&since={urllib.parse.quote(since, safe='')}"
    )
    contexto = ssl.create_default_context()
    with urllib.request.urlopen(url, timeout=_TIMEOUT, context=contexto) as resp:
        return [json.loads(linea) for linea in resp if linea.strip()]


def _aplicar_comandos(mensajes, token):
    ids = set()
    for mensaje in mensajes:
        if mensaje.get("event") != "message":
            continue
        comando = _parse_comando(mensaje.get("message"))
        if comando is None:
            continue
        tarea_id, recibido = comando
        if hmac.compare_digest(recibido.encode(), token.encode()):
            ids.add(tarea_id)

    if not ids:
        return 0

    tareas = storage.cargar_tareas()
    aplicadas = 0
    for tarea in tareas:
        if tarea.get("id") in ids and not tarea.get("completada"):
            tarea["completada"] = True
            aplicadas += 1
    if aplicadas:
        storage.guardar_tareas(tareas)
    return aplicadas


def procesar_comandos(silencioso=False):
    """Lee los comandos nuevos de ntfy y marca las tareas completadas.

    Devuelve cuántas tareas se completaron. Nunca lanza errores de red.
    """
    config = storage.cargar_config()
    cmd_topic = config.get("ntfy_cmd_topic")
    token = config.get("ntfy_cmd_token")
    if not cmd_topic or not token:
        return 0

    server = (
        os.environ.get("NTFY_SERVER")
        or config.get("ntfy_server")
        or paths.NTFY_SERVER_DEFAULT
    )
    since = config.get("ntfy_last_id") or "all"

    try:
        mensajes = _leer_mensajes(server, cmd_topic, since)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        if not silencioso:
            print(
                Fore.RED + f"  No se pudo sincronizar: {exc}" + Style.RESET_ALL
            )
        return 0

    aplicadas = _aplicar_comandos(mensajes, token)

    ultimo = next(
        (
            mensaje.get("id")
            for mensaje in reversed(mensajes)
            if mensaje.get("event") == "message" and mensaje.get("id")
        ),
        None,
    )
    if ultimo:
        storage.actualizar_config({"ntfy_last_id": ultimo})

    if aplicadas:
        print(
            Fore.GREEN
            + f"  ✔ {aplicadas} tarea(s) completada(s) desde el móvil."
            + Style.RESET_ALL
        )
    elif not silencioso:
        print("  No hay tareas nuevas completadas desde el móvil.")
    return aplicadas
