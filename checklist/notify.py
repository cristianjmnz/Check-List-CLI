"""Notificaciones push vía ntfy.sh y recordatorio diario (launchd)."""

import json
import os
import secrets
import ssl
import sys
import urllib.request
from pathlib import Path

from colorama import Fore, Style

from . import models, paths, storage

_PRIORIDAD_NTFY = {"alta": "high", "media": "default", "baja": "low"}
_HORA_DEFECTO = "08:00"


def obtener_ntfy():
    config = storage.cargar_config()
    topic = os.environ.get("NTFY_TOPIC") or config.get("ntfy_topic") or ""
    server = (
        os.environ.get("NTFY_SERVER")
        or config.get("ntfy_server")
        or paths.NTFY_SERVER_DEFAULT
    )
    return topic.strip(), server.strip()


def generar_tema():
    return "checklist-" + secrets.token_hex(4)


def _header_seguro(valor):
    return valor.encode("latin-1", errors="ignore").decode("latin-1")


def hora_recordatorio():
    """Hora 'HH:MM' configurada para el recordatorio (default 08:00)."""
    config = storage.cargar_config()
    return models.normalizar_hora(config.get("recordatorio_hora")) or _HORA_DEFECTO


def enviar_notificacion(titulo, mensaje, tags="memo", prioridad=None, action_url=None):
    topic, server = obtener_ntfy()
    if not topic:
        print(
            Fore.RED
            + "  No hay tema ntfy configurado. Ve a '8. Notificaciones' para crearlo."
            + Style.RESET_ALL
        )
        return False

    url = f"{server.rstrip('/')}/{topic}"
    req = urllib.request.Request(url, data=mensaje.encode("utf-8"), method="POST")
    req.add_header("Title", _header_seguro(titulo))
    if tags:
        req.add_header("Tags", _header_seguro(tags))
    if prioridad and prioridad != "default":
        req.add_header("Priority", _header_seguro(prioridad))
    if action_url:
        acciones = [
            {"action": "view", "label": "Abrir", "url": action_url}
        ]
        req.add_header("Actions", _header_seguro(json.dumps(acciones)))

    try:
        contexto = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=5, context=contexto) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(Fore.RED + f"  No se pudo enviar la notificación: {e}" + Style.RESET_ALL)
        return False


def construir_mensaje_pendientes(tareas):
    """Devuelve (titulo, cuerpo, tags, prioridad_ntfy) del resumen de pendientes."""
    pendientes = models.obtener_pendientes_ordenados(tareas)

    if not pendientes:
        return "Check List", "Todo al día 🎉", "white_check_mark", "default"

    n = len(pendientes)
    lineas = [
        f"Tienes {n} tarea{'s' if n > 1 else ''} pendiente{'s' if n > 1 else ''}:",
        "",
    ]
    for _, t in pendientes:
        item = t["texto"]
        if t.get("tag"):
            item += f" [{t['tag']}]"
        if t.get("prioridad") == "alta":
            item += " ⚠"
        lineas.append(f"• {item}")

    cuerpo = "\n".join(lineas)
    if len(cuerpo.encode("utf-8")) > paths.NTFY_LIMITE_BYTES:
        corte = cuerpo.encode("utf-8")[: paths.NTFY_LIMITE_BYTES].decode(
            "utf-8", errors="ignore"
        )
        restantes = cuerpo.count("\n") - corte.count("\n")
        cuerpo = corte + f"\n… y {max(restantes, 1)} más"

    prioridad = _PRIORIDAD_NTFY.get(models.prioridad_max(pendientes), "default")
    return "Check List", cuerpo, "memo", prioridad


def enviar_pendientes(tareas):
    titulo, cuerpo, ntfy_tags, prioridad = construir_mensaje_pendientes(tareas)
    topic, server = obtener_ntfy()
    action_url = f"{server.rstrip('/')}/{topic}" if topic else None
    return enviar_notificacion(
        titulo, cuerpo, tags=ntfy_tags, prioridad=prioridad, action_url=action_url
    )


def instalar_recordatorio():
    label = "com.cristianjmnz.checklist"
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = plist_dir / f"{label}.plist"

    if sys.platform != "darwin":
        print(
            Fore.RED
            + "  El recordatorio automático solo está disponible en macOS."
            + Style.RESET_ALL
        )
        return

    topic, _ = obtener_ntfy()
    if not topic:
        print(
            Fore.RED
            + "  Primero configura un tema ntfy ('1. Configurar tema')."
            + Style.RESET_ALL
        )
        return

    plist_dir.mkdir(parents=True, exist_ok=True)

    hora = hora_recordatorio()
    hora_parts = hora.split(":")

    if getattr(sys, "frozen", False):
        args = [sys.executable, "--notify-pendientes"]
    else:
        args = [
            sys.executable,
            str(paths.PROJECT_ROOT / "main.py"),
            "--notify-pendientes",
        ]
    args_xml = "".join(f"\n        <string>{a}</string>" for a in args)

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>{args_xml}
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{int(hora_parts[0])}</integer>
        <key>Minute</key>
        <integer>{int(hora_parts[1])}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/checklist.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/checklist.err</string>
</dict>
</plist>
"""
    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist)

    os.system(f'launchctl unload "{plist_path}" 2>/dev/null')
    codigo = os.system(f'launchctl load "{plist_path}"')
    if codigo == 0:
        print(
            Fore.GREEN
            + f"  ✔ Recordatorio diario instalado ({hora})."
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.RED
            + "  No se pudo cargar el recordatorio. Archivo creado en:"
            + Style.RESET_ALL
        )
    print(Fore.WHITE + f"      {plist_path}" + Style.RESET_ALL)
