import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import argparse
import json
import os
import secrets
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path

if getattr(sys, "frozen", False):
    try:
        from platformdirs import user_data_dir
        DATA_DIR = Path(user_data_dir("Check-List-CLI", roaming=False))
    except Exception:
        DATA_DIR = Path.home() / ".checklist"
else:
    DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE = DATA_DIR / "tareas.json"
FILE_TAGS = DATA_DIR / "tags.json"
FILE_CONFIG = DATA_DIR / "config.json"

NTFY_SERVER_DEFAULT = "https://ntfy.sh"
NTFY_LIMITE_BYTES = 3900

from colorama import init, Fore, Back, Style
init()

COLORES_DISPONIBLES = {
    "rojo": Fore.RED,
    "verde": Fore.GREEN,
    "amarillo": Fore.YELLOW,
    "azul": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "blanco": Fore.WHITE,
}

# ─── ASCII Art ────────────────────────────────────────────────────────────────

ASCII_CHECK = [
    r"   ________              __  ",
    r"  / ____/ /_  ___  _____/ /__",
    r" / /   / __ \/ _ \/ ___/ //_/",
    r"/ /___/ / / /  __/ /__/ ,<   ",
    r"\____/_/ /_/\___/\___/_/|_|  ",
]

ASCII_LIST_CLI = [
    r"    __    _      __      ________    ____",
    r"   / /   (_)____/ /_    / ____/ /   /  _/",
    r"  / /   / / ___/ __/   / /   / /    / /  ",
    r" / /___/ (__  ) /_    / /___/ /____/ /   ",
    r"/_____/_/____/\__/    \____/_____/___/   ",
]
 
GITHUB_URL = "https://github.com/cristianjmnz"
 
def mostrar_banner():
    print()
    for line in ASCII_CHECK:
        print(Fore.GREEN + line + Style.RESET_ALL)
    for i, line in enumerate(ASCII_LIST_CLI):
        if i == 1:
            print(Fore.CYAN + line + "   " + Style.RESET_ALL + Fore.GREEN + Style.BRIGHT + GITHUB_URL + Style.RESET_ALL)
        elif i == 2:
            print(Fore.CYAN + line + "   " + Style.RESET_ALL + Fore.WHITE + "Deep clean your task list." + Style.RESET_ALL)
        else:
            print(Fore.CYAN + line + Style.RESET_ALL)
    print()

def mostrar_barra_atajos():
    atajos = [
        ("1-8", "Seleccionar"),
        ("0",   "Salir"),
        ("Enter", "Confirmar"),
    ]
    partes = "   ".join(
        Fore.GREEN + Style.BRIGHT + f"[{k}]" + Style.RESET_ALL +
        Fore.WHITE + f" {v}" + Style.RESET_ALL
        for k, v in atajos
    )
    print(Fore.GREEN + "  " + "─" * 40 + Style.RESET_ALL)
    print("  " + partes)

# ─── Menú principal ───────────────────────────────────────────────────────────

def mostrar_menu():
    mostrar_banner()
    print(Fore.GREEN + "  " + "─" * 36 + Style.RESET_ALL)

    opciones = [
        ("1", "Añadir tarea"),
        ("2", "Listar tareas"),
        ("3", "Buscar tarea"),
        ("4", "Marcar como completada"),
        ("5", "Editar tarea"),
        ("6", "Eliminar tarea"),
        ("7", "Gestionar tags"),
        ("8", "Notificaciones"),
        ("0", "Salir"),
    ]
    for num, texto in opciones:
        separador = Fore.GREEN + "." + Style.RESET_ALL
        print(
            "  " +
            Fore.CYAN + Style.BRIGHT + num + Style.RESET_ALL +
            separador +
            "  " + Fore.WHITE + texto + Style.RESET_ALL
        )

    print(Fore.GREEN + "  " + "─" * 36 + Style.RESET_ALL)
    mostrar_barra_atajos()

# ─── Tags ─────────────────────────────────────────────────────────────────────

def cargar_tags():
    if not os.path.exists(FILE_TAGS):
        return {}
    try:
        with open(FILE_TAGS, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeError, OSError):
        try:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = str(FILE_TAGS) + f".corrupt-{ts}"
            os.replace(FILE_TAGS, backup)
            print(Fore.RED + f"  Archivo tags corrupto. Se respaldó como {backup}" + Style.RESET_ALL)
        except Exception:
            pass
        return {}
    if not isinstance(data, dict):
        try:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = str(FILE_TAGS) + f".corrupt-{ts}"
            os.replace(FILE_TAGS, backup)
            print(Fore.RED + f"  Archivo tags corrupto (formato inesperado). Se respaldó como {backup}" + Style.RESET_ALL)
        except Exception:
            pass
        return {}
    tags = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str) and v in COLORES_DISPONIBLES:
            tags[k] = v
    return tags

def guardar_tags(tags):
    tmp = str(FILE_TAGS) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=4, ensure_ascii=False)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, FILE_TAGS)

def gestionar_tags(tags):
    while True:
        print(Fore.GREEN + "\n  ── Gestionar tags ──" + Style.RESET_ALL)
        print("  " + Fore.CYAN + "1." + Style.RESET_ALL + " Ver tags")
        print("  " + Fore.CYAN + "2." + Style.RESET_ALL + " Crear tag")
        print("  " + Fore.CYAN + "3." + Style.RESET_ALL + " Eliminar tag")
        print("  " + Fore.CYAN + "0." + Style.RESET_ALL + " Volver")

        opcion = input("\n  Selecciona una opción: ")

        if opcion == "1":
            if not tags:
                print("  No hay tags creados.")
            else:
                for nombre, color in tags.items():
                    print("  " + COLORES_DISPONIBLES[color] + f"● {nombre}" + Style.RESET_ALL)

        elif opcion == "2":
            nombre = input("  Nombre del tag: ").strip().lower()
            if not nombre:
                print("  El nombre no puede estar vacío.")
                continue
            if nombre in tags:
                print(Fore.RED + "  Ya existe un tag con ese nombre." + Style.RESET_ALL)
                continue

            print("  Colores disponibles: " + ", ".join(COLORES_DISPONIBLES.keys()))
            color = input("  Color: ").strip().lower()
            if color not in COLORES_DISPONIBLES:
                print(Fore.RED + "  Color no válido." + Style.RESET_ALL)
                continue

            tags[nombre] = color
            guardar_tags(tags)
            print(COLORES_DISPONIBLES[color] + f"  ✔ Tag '{nombre}' creado." + Style.RESET_ALL)

        elif opcion == "3":
            if not tags:
                print("  No hay tags para eliminar.")
                continue

            for nombre, color in tags.items():
                print("  " + COLORES_DISPONIBLES[color] + f"● {nombre}" + Style.RESET_ALL)

            nombre = input("  Nombre del tag a eliminar: ").strip().lower()
            if nombre not in tags:
                print(Fore.RED + "  Ese tag no existe." + Style.RESET_ALL)
                continue

            del tags[nombre]
            guardar_tags(tags)
            print(Fore.GREEN + f"  ✔ Tag '{nombre}' eliminado." + Style.RESET_ALL)

        elif opcion == "0":
            break

# ─── Utilidades ───────────────────────────────────────────────────────────────

def limpiar_pantalla():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def tiempo_relativo(fecha_str):
    try:
        ahora = datetime.now()
        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00").replace("+00:00", ""))
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

# ─── Tareas ───────────────────────────────────────────────────────────────────

def cargar_tareas():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeError, OSError):
        try:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = str(FILE) + f".corrupt-{ts}"
            os.replace(FILE, backup)
            print(Fore.RED + f"  Archivo corrupto. Se respaldó como {backup}" + Style.RESET_ALL)
        except Exception:
            pass
        return []
    if not isinstance(data, list):
        try:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = str(FILE) + f".corrupt-{ts}"
            os.replace(FILE, backup)
            print(Fore.RED + f"  Archivo corrupto (formato inesperado). Se respaldó como {backup}" + Style.RESET_ALL)
        except Exception:
            pass
        return []
    tareas = []
    for t in data:
        if not isinstance(t, dict):
            continue
        tarea = {
            "texto": t.get("texto", "") if isinstance(t.get("texto"), str) else str(t.get("texto", "")),
            "completada": bool(t.get("completada", False)),
            "fecha": t.get("fecha") if isinstance(t.get("fecha"), str) else None,
            "tag": t.get("tag") if isinstance(t.get("tag"), str) else None,
        }
        tareas.append(tarea)
    return tareas

def guardar_tareas(tareas):
    tmp = str(FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=4, ensure_ascii=False)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, FILE)

def obtener_pendientes_ordenados(tareas):
    pendientes = [(i, t) for i, t in enumerate(tareas, 1) if not t["completada"]]
    pendientes.sort(key=lambda x: x[1].get("fecha", ""), reverse=True)
    return pendientes

def añadir_tarea(tareas, tags):
    texto = input("\n  Escribe la tarea: ").strip()
    if not texto:
        print("  No puedes añadir una tarea vacía.")
        return

    tag = None
    if tags:
        print("  Tags disponibles: ", end="")
        for nombre, color in tags.items():
            print(COLORES_DISPONIBLES[color] + nombre + Style.RESET_ALL, end="  ")
        print()
        entrada = input("  Tag (Enter para ninguno): ").strip().lower()
        if entrada and entrada in tags:
            tag = entrada
        elif entrada:
            print(Fore.RED + "  Tag no reconocido, se guardará sin tag." + Style.RESET_ALL)

    tareas.append({
        "texto": texto,
        "completada": False,
        "fecha": datetime.now().isoformat(),
        "tag": tag
    })
    guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tarea añadida." + Style.RESET_ALL)

def listar_tareas(tareas, tags):
    if not tareas:
        print("\n  No hay tareas")
        return

    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.GREEN + "\n  Todas las tareas están completadas. ¡Buen trabajo!" + Style.RESET_ALL)
        return

    print()
    for contador, (_, t) in enumerate(pendientes, 1):
        estado = Fore.YELLOW + "○" + Style.RESET_ALL

        if "fecha" in t:
            tiempo = Fore.CYAN + f"({tiempo_relativo(t['fecha'])})" + Style.RESET_ALL
        else:
            tiempo = Fore.CYAN + "(Sin fecha)" + Style.RESET_ALL

        tag_str = ""
        if t.get("tag") and t["tag"] in tags:
            color = COLORES_DISPONIBLES.get(tags[t["tag"]], "")
            tag_str = color + f"[{t['tag']}]" + Style.RESET_ALL

        print(f"  {contador:>2} | {estado} {t['texto']:<30} {tiempo} {tag_str}")

def marcar_completada(tareas, tags):
    pendientes = obtener_pendientes_ordenados(tareas)
    if not pendientes:
        print("\n  No hay tareas pendientes para marcar como completadas.")
        return

    listar_tareas(tareas, tags)

    try:
        idx = int(input("\n  Número de tarea: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "  Número fuera de rango" + Style.RESET_ALL)
            return

        indice_real, _ = pendientes[idx - 1]
        tareas[indice_real - 1]["completada"] = True
        guardar_tareas(tareas)
        print(Fore.GREEN + "  ✔ Tarea completada." + Style.RESET_ALL)

    except ValueError:
        print("  Número no válido")

def eliminar_tarea(tareas, tags):
    if not tareas:
        print("\n  No hay tareas para eliminar.")
        return

    pendientes = obtener_pendientes_ordenados(tareas)
    if not pendientes:
        print("\n  No hay tareas pendientes para eliminar.")
        return

    listar_tareas(tareas, tags)

    entrada = input("\n  Selecciona tareas a eliminar (ej: 1 3 5): ").split()

    try:
        numeros = [int(n) for n in entrada]
    except ValueError:
        print("  Debes introducir solo números.")
        return

    indices_validos = []
    for n in numeros:
        if 1 <= n <= len(pendientes):
            idx_real = pendientes[n - 1][0]
            if idx_real not in indices_validos:
                indices_validos.append(idx_real)

    if not indices_validos:
        print(Fore.RED + "  No hay números válidos seleccionados." + Style.RESET_ALL)
        return

    confirmacion = input("  ¿Seguro que quieres eliminar estas tareas? (s/n): ").lower()
    if confirmacion != "s":
        print("  Operación cancelada.")
        return

    indices_validos.sort(reverse=True)

    for indice_real in indices_validos:
        tareas.pop(indice_real - 1)

    guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tareas eliminadas." + Style.RESET_ALL)

def editar_tarea(tareas, tags):
    if not tareas:
        print("\n  No hay tareas para editar.")
        return

    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.RED + "  No hay tareas pendientes para editar." + Style.RESET_ALL)
        return

    listar_tareas(tareas, tags)

    try:
        idx = int(input("\n  Número de tarea a editar: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "  Número fuera de rango." + Style.RESET_ALL)
            return

        indice_real, tarea = pendientes[idx - 1]
        print(f"  Texto actual: {tarea['texto']}")
        nuevo_texto = input("  Nuevo texto (Enter para mantener): ").strip()

        if nuevo_texto:
            tareas[indice_real - 1]["texto"] = nuevo_texto

        if tags:
            print("  Tags disponibles: ", end="")
            for nombre, color in tags.items():
                print(COLORES_DISPONIBLES[color] + nombre + Style.RESET_ALL, end="  ")
            print()
            entrada = input("  Nuevo tag (Enter para mantener, '-' para quitar): ").strip().lower()
            if entrada == "-":
                tareas[indice_real - 1]["tag"] = None
            elif entrada and entrada in tags:
                tareas[indice_real - 1]["tag"] = entrada
            elif entrada:
                print(Fore.RED + "  Tag no reconocido, se mantiene el tag actual." + Style.RESET_ALL)

        guardar_tareas(tareas)
        print(Fore.GREEN + "  ✔ Tarea actualizada." + Style.RESET_ALL)

    except ValueError:
        print("  Debes introducir un número válido.")

def buscar_tarea(tareas):
    palabra = input("  ¿Qué tarea buscas?: ").strip().lower()

    if not palabra:
        print("  Tienes que escribir mínimo una letra.")
        return

    if not tareas:
        print("\n  No hay tareas guardadas.")
        return

    encontrado = False

    for i, t in enumerate(tareas, 1):
        if palabra in t["texto"].lower():
            estado = Fore.GREEN + "✔" + Style.RESET_ALL if t["completada"] else Fore.YELLOW + "○" + Style.RESET_ALL
            print(f"  {i}. [{estado}] {t['texto']}")
            encontrado = True

    if not encontrado:
        print(Fore.RED + "  No se encontraron tareas con esa palabra." + Style.RESET_ALL)

# ─── Notificaciones (ntfy) ────────────────────────────────────────────────────

def cargar_config():
    if not os.path.exists(FILE_CONFIG):
        return {}
    try:
        with open(FILE_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeError, OSError):
        try:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = str(FILE_CONFIG) + f".corrupt-{ts}"
            os.replace(FILE_CONFIG, backup)
            print(Fore.RED + f"  Config corrupta. Se respaldó como {backup}" + Style.RESET_ALL)
        except Exception:
            pass
        return {}
    if not isinstance(data, dict):
        return {}
    cfg = {}
    if isinstance(data.get("ntfy_topic"), str):
        cfg["ntfy_topic"] = data["ntfy_topic"]
    if isinstance(data.get("ntfy_server"), str):
        cfg["ntfy_server"] = data["ntfy_server"]
    return cfg

def guardar_config(config):
    tmp = str(FILE_CONFIG) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, FILE_CONFIG)

def obtener_ntfy():
    config = cargar_config()
    topic = os.environ.get("NTFY_TOPIC") or config.get("ntfy_topic") or ""
    server = os.environ.get("NTFY_SERVER") or config.get("ntfy_server") or NTFY_SERVER_DEFAULT
    return topic.strip(), server.strip()

def generar_tema():
    return "checklist-" + secrets.token_hex(4)

def _header_seguro(valor):
    return valor.encode("latin-1", errors="ignore").decode("latin-1")

def enviar_notificacion(titulo, mensaje, tags="memo"):
    topic, server = obtener_ntfy()
    if not topic:
        print(Fore.RED + "  No hay tema ntfy configurado. Ve a '8. Notificaciones' para crearlo." + Style.RESET_ALL)
        return False

    url = f"{server.rstrip('/')}/{topic}"
    req = urllib.request.Request(url, data=mensaje.encode("utf-8"), method="POST")
    req.add_header("Title", _header_seguro(titulo))
    if tags:
        req.add_header("Tags", _header_seguro(tags))

    try:
        contexto = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=5, context=contexto) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(Fore.RED + f"  No se pudo enviar la notificación: {e}" + Style.RESET_ALL)
        return False

def enviar_pendientes(tareas, tags):
    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        return enviar_notificacion("Check List", "Todo al día 🎉", tags="white_check_mark")

    n = len(pendientes)
    lineas = [f"Tienes {n} tarea{'s' if n > 1 else ''} pendiente{'s' if n > 1 else ''}:", ""]
    for _, t in pendientes:
        item = t["texto"]
        if t.get("tag"):
            item += f" [{t['tag']}]"
        lineas.append(f"• {item}")

    cuerpo = "\n".join(lineas)
    if len(cuerpo.encode("utf-8")) > NTFY_LIMITE_BYTES:
        corte = cuerpo.encode("utf-8")[:NTFY_LIMITE_BYTES].decode("utf-8", errors="ignore")
        restantes = cuerpo.count("\n") - corte.count("\n")
        cuerpo = corte + f"\n… y {max(restantes, 1)} más"

    return enviar_notificacion("Check List", cuerpo, tags="memo")

def configurar_tema():
    topic, server = obtener_ntfy()
    config = cargar_config()
    if "ntfy_server" not in config:
        config["ntfy_server"] = server

    if topic:
        print(f"  Tema actual: {Fore.CYAN}{topic}{Style.RESET_ALL}")
        respuesta = input("  ¿Generar uno nuevo? (s/n): ").strip().lower()
        if respuesta != "s":
            mostrar_instrucciones_ntfy(topic)
            return

    nuevo = generar_tema()
    config["ntfy_topic"] = nuevo
    guardar_config(config)
    print(Fore.GREEN + f"\n  ✔ Tema generado: {nuevo}" + Style.RESET_ALL)
    mostrar_instrucciones_ntfy(nuevo)

def mostrar_instrucciones_ntfy(topic):
    print()
    print(Fore.CYAN + "  Instala la app 'ntfy' en tu móvil (App Store / Play Store / F-Droid)." + Style.RESET_ALL)
    print(Fore.CYAN + "  Suscríbete a este tema:" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + f"      {topic}" + Style.RESET_ALL)
    print(Fore.CYAN + "  O abre directamente:" + Style.RESET_ALL)
    print(Fore.WHITE + f"      https://ntfy.sh/{topic}" + Style.RESET_ALL)

def instalar_recordatorio():
    label = "com.cristianjmnz.checklist"
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = plist_dir / f"{label}.plist"

    if not sys.platform == "darwin":
        print(Fore.RED + "  El recordatorio automático solo está disponible en macOS." + Style.RESET_ALL)
        return

    topic, _ = obtener_ntfy()
    if not topic:
        print(Fore.RED + "  Primero configura un tema ntfy ('1. Configurar tema')." + Style.RESET_ALL)
        return

    plist_dir.mkdir(parents=True, exist_ok=True)

    if getattr(sys, "frozen", False):
        args = [sys.executable, "--notify-pendientes"]
    else:
        args = [sys.executable, os.path.abspath(__file__), "--notify-pendientes"]
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
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
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
        print(Fore.GREEN + f"  ✔ Recordatorio diario instalado (8:00)." + Style.RESET_ALL)
        print(Fore.WHITE + f"      {plist_path}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "  No se pudo cargar el recordatorio. Archivo creado en:" + Style.RESET_ALL)
        print(Fore.WHITE + f"      {plist_path}" + Style.RESET_ALL)

def gestionar_notificaciones(tareas, tags):
    while True:
        print(Fore.GREEN + "\n  ── Notificaciones ──" + Style.RESET_ALL)
        print("  " + Fore.CYAN + "1." + Style.RESET_ALL + " Configurar tema")
        print("  " + Fore.CYAN + "2." + Style.RESET_ALL + " Enviar pendientes al móvil")
        print("  " + Fore.CYAN + "3." + Style.RESET_ALL + " Instalar recordatorio diario (8:00)")
        print("  " + Fore.CYAN + "0." + Style.RESET_ALL + " Volver")

        opcion = input("\n  Selecciona una opción: ").strip()

        if opcion == "1":
            configurar_tema()
        elif opcion == "2":
            if enviar_pendientes(tareas, tags):
                print(Fore.GREEN + "  ✔ Notificación enviada." + Style.RESET_ALL)
        elif opcion == "3":
            instalar_recordatorio()
        elif opcion == "0":
            break

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    try:
        tareas = cargar_tareas()
        tags   = cargar_tags()

        while True:
            limpiar_pantalla()
            pendientes = sum(1 for t in tareas if not t.get("completada", False))
            mostrar_menu()
            print(Fore.CYAN + f"\n  📋 {pendientes} tarea(s) pendiente(s)\n" + Style.RESET_ALL)
            try:
                opcion = input("  Selecciona una opción: ")
            except (EOFError, KeyboardInterrupt):
                print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
                break
            opcion = opcion.strip()

            if opcion == "1":
                añadir_tarea(tareas, tags)
            elif opcion == "2":
                listar_tareas(tareas, tags)
            elif opcion == "3":
                buscar_tarea(tareas)
            elif opcion == "4":
                marcar_completada(tareas, tags)
            elif opcion == "5":
                editar_tarea(tareas, tags)
            elif opcion == "6":
                eliminar_tarea(tareas, tags)
            elif opcion == "7":
                gestionar_tags(tags)
            elif opcion == "8":
                gestionar_notificaciones(tareas, tags)
            elif opcion == "0":
                print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "  Opción no válida." + Style.RESET_ALL)

            try:
                input(Fore.GREEN + "\n  Presiona Enter para continuar..." + Style.RESET_ALL)
            except (EOFError, KeyboardInterrupt):
                print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
                break
    except (KeyboardInterrupt, EOFError):
        print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)

def cli():
    parser = argparse.ArgumentParser(
        prog="checklist",
        description="Check List CLI — gestor de tareas de terminal con notificaciones ntfy.",
    )
    parser.add_argument(
        "--notify-pendientes",
        action="store_true",
        help="Envía las tareas pendientes por ntfy y sale (para cron/launchd).",
    )
    parser.add_argument(
        "--set-topic",
        metavar="TEMA",
        help="Guarda el tema ntfy indicado y sale.",
    )
    args = parser.parse_args()

    if args.set_topic:
        config = cargar_config()
        config["ntfy_topic"] = args.set_topic.strip()
        config.setdefault("ntfy_server", NTFY_SERVER_DEFAULT)
        guardar_config(config)
        print(Fore.GREEN + f"✔ Tema ntfy guardado: {args.set_topic.strip()}" + Style.RESET_ALL)
        sys.exit(0)

    if args.notify_pendientes:
        tareas = cargar_tareas()
        tags = cargar_tags()
        sys.exit(0 if enviar_pendientes(tareas, tags) else 1)

    main()

if __name__ == "__main__":
    cli()