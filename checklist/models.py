"""Lógica pura sobre tareas, tags y configuración (sin input/print)."""

import re
from datetime import datetime

PRIORIDADES = ("alta", "media", "baja")
_PRIORIDAD_ORDEN = {"alta": 3, "media": 2, "baja": 1}
_HORA_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def normalizar_prioridad(v):
    """Devuelve 'alta'/'media'/'baja' (default 'media')."""
    if isinstance(v, str) and v in PRIORIDADES:
        return v
    return "media"


def normalizar_tarea(t):
    """Devuelve una tarea con claves garantizadas, o None si no es válida."""
    if not isinstance(t, dict):
        return None
    texto = t.get("texto", "")
    if not isinstance(texto, str):
        texto = str(texto)
    tarea = {
        "texto": texto,
        "completada": bool(t.get("completada", False)),
        "fecha": t.get("fecha") if isinstance(t.get("fecha"), str) else None,
        "tag": t.get("tag") if isinstance(t.get("tag"), str) else None,
        "prioridad": normalizar_prioridad(t.get("prioridad")),
    }
    identificador = t.get("id")
    if isinstance(identificador, int) and identificador >= 1:
        tarea["id"] = identificador
    return tarea


def normalizar_tags(data, colores_validos):
    """Filtra un dict crudo dejando solo pares nombre/color válidos."""
    if not isinstance(data, dict):
        return {}
    return {
        k: v
        for k, v in data.items()
        if isinstance(k, str) and isinstance(v, str) and v in colores_validos
    }


def normalizar_config(data):
    """Filtra un dict crudo de configuración dejando solo claves conocidas."""
    if not isinstance(data, dict):
        return {}
    cfg = {}
    if isinstance(data.get("ntfy_topic"), str):
        cfg["ntfy_topic"] = data["ntfy_topic"]
    if isinstance(data.get("ntfy_server"), str):
        cfg["ntfy_server"] = data["ntfy_server"]
    for clave in ("ntfy_cmd_topic", "ntfy_cmd_token", "ntfy_last_id"):
        valor = data.get(clave)
        if isinstance(valor, str) and valor.strip():
            cfg[clave] = valor.strip()
    hora = normalizar_hora(data.get("recordatorio_hora"))
    if hora:
        cfg["recordatorio_hora"] = hora
    return cfg


def normalizar_hora(valor):
    """Devuelve 'HH:MM' normalizado a 2 dígitos, o None si no es válido."""
    if not isinstance(valor, str):
        return None
    m = _HORA_RE.match(valor.strip())
    if not m:
        return None
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def obtener_pendientes_ordenados(tareas):
    """Lista de (indice_real_1based, tarea) pendientes, más recientes primero."""
    pendientes = [
        (i, t) for i, t in enumerate(tareas, 1) if not t.get("completada", False)
    ]
    pendientes.sort(key=lambda x: x[1].get("fecha") or "", reverse=True)
    return pendientes


def indice_real_de_pendiente(tareas, numero):
    """Traduce el número mostrado en la lista al índice real (1-based) o None."""
    pendientes = obtener_pendientes_ordenados(tareas)
    if 1 <= numero <= len(pendientes):
        return pendientes[numero - 1][0]
    return None


def crear_tarea(texto, tag=None, prioridad=None):
    """Construye una tarea nueva ya normalizada."""
    return {
        "texto": texto,
        "completada": False,
        "fecha": datetime.now().isoformat(),
        "tag": tag,
        "prioridad": normalizar_prioridad(prioridad),
    }


def prioridad_max(pendientes):
    """Menor etiqueta de prioridad entre las tareas pendientes, o None."""
    valores = [
        _PRIORIDAD_ORDEN.get(t.get("prioridad"), 2)
        for _, t in pendientes
        if not t.get("completada", False)
    ]
    if not valores:
        return None
    mayor = max(valores)
    return next(k for k, v in _PRIORIDAD_ORDEN.items() if v == mayor)


def tiempo_relativo(fecha_str):
    try:
        ahora = datetime.now()
        fecha = datetime.fromisoformat(
            fecha_str.replace("Z", "+00:00").replace("+00:00", "")
        )
        if fecha.tzinfo is not None:
            fecha = fecha.replace(tzinfo=None)
        diferencia = ahora - fecha
        segundos = int(diferencia.total_seconds())
        if segundos < 0:
            return "En el futuro"
        if segundos < 60:
            return "Hace un momento"
        minutos = segundos // 60
        if minutos < 60:
            return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        horas = minutos // 60
        if horas < 24:
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        dias = horas // 24
        if dias < 7:
            return f"Hace {dias} dia{'s' if dias > 1 else ''}"
        semanas = dias // 7
        if semanas < 4:
            return f"Hace {semanas} semana{'s' if semanas > 1 else ''}"
        meses = dias // 30
        if meses < 12:
            return f"Hace {meses} mes{'es' if meses > 1 else ''}"
        anos = dias // 365
        return f"Hace {anos} año{'s' if anos > 1 else ''}"
    except Exception:
        return "(fecha inválida)"
