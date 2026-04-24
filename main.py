import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os

FILE = "tareas.json"
FILE_TAGS = "tags.json"

from colorama import init, Fore, Back, Style
init()

from datetime import datetime

COLORES_DISPONIBLES = {
    "rojo": Fore.RED,
    "verde": Fore.GREEN,
    "amarillo": Fore.YELLOW,
    "azul": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "blanco": Fore.WHITE,
}

from database import crear_db

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
        ("1-7", "Seleccionar"),
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
    with open(FILE_TAGS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_tags(tags):
    with open(FILE_TAGS, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=4, ensure_ascii=False)

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
    os.system("cls" if os.name == "nt" else "clear")

def tiempo_relativo(fecha_str):
    ahora = datetime.now()
    fecha = datetime.fromisoformat(fecha_str)
    diferencia = ahora - fecha

    segundos = int(diferencia.total_seconds())
    minutos = segundos // 60
    horas = minutos // 60
    dias = horas // 24
    semanas = dias // 7
    meses = dias // 30

    if segundos < 60:
        return "Hace un momento"
    elif minutos < 60:
        return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
    elif horas < 24:
        return f"Hace {horas} hora{'s' if horas > 1 else ''}"
    elif dias < 7:
        return f"Hace {dias} dia{'s' if dias > 1 else ''}"
    elif semanas < 4:
        return f"Hace {semanas} semana{'s' if semanas > 1 else ''}"
    else:
        return f"Hace {meses} mes{'es' if meses > 1 else ''}"

# ─── Tareas ───────────────────────────────────────────────────────────────────

def cargar_tareas():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_tareas(tareas):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=4, ensure_ascii=False)

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
            color = COLORES_DISPONIBLES[tags[t["tag"]]]
            tag_str = color + f"[{t['tag']}]" + Style.RESET_ALL

        print(f"  {contador:>2} | {estado} {t['texto']:<30} {tiempo} {tag_str}")

def marcar_completada(tareas, tags):
    listar_tareas(tareas, tags)
    pendientes = obtener_pendientes_ordenados(tareas)

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

    listar_tareas(tareas, tags)
    pendientes = obtener_pendientes_ordenados(tareas)

    entrada = input("\n  Selecciona tareas a eliminar (ej: 1 3 5): ").split()

    try:
        numeros = [int(n) for n in entrada]
    except ValueError:
        print("  Debes introducir solo números.")
        return

    confirmacion = input("  ¿Seguro que quieres eliminar estas tareas? (s/n): ").lower()
    if confirmacion != "s":
        print("  Operación cancelada.")
        return

    indices_a_borrar = []
    for n in numeros:
        if 1 <= n <= len(pendientes):
            indices_a_borrar.append(pendientes[n - 1][0])
        else:
            print(Fore.RED + f"  Número {n} fuera de rango" + Style.RESET_ALL)

    indices_a_borrar.sort(reverse=True)

    for indice_real in indices_a_borrar:
        tareas.pop(indice_real - 1)

    guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tareas eliminadas." + Style.RESET_ALL)

def editar_tarea(tareas, tags):
    if not tareas:
        print("\n  No hay tareas para editar.")
        return

    listar_tareas(tareas, tags)
    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.RED + "  No hay tareas pendientes para editar." + Style.RESET_ALL)
        return

    try:
        idx = int(input("\n  Número de tarea a editar: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "  Número fuera de rango." + Style.RESET_ALL)
            return

        indice_real, tarea = pendientes[idx - 1]
        print(f"  Texto actual: {tarea['texto']}")
        nuevo_texto = input("  Nuevo texto: ").strip()

        if not nuevo_texto:
            print("  No puedes dejar la tarea vacía.")
            return

        tareas[indice_real - 1]["texto"] = nuevo_texto
        guardar_tareas(tareas)
        print(Fore.GREEN + "  ✏️  Tarea actualizada." + Style.RESET_ALL)

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

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    crear_db()
    tareas = cargar_tareas()
    tags   = cargar_tags()

    while True:
        limpiar_pantalla()
        pendientes = sum(1 for t in tareas if not t["completada"])
        mostrar_menu()
        print(Fore.CYAN + f"\n  📋 {pendientes} tarea(s) pendiente(s)\n" + Style.RESET_ALL)
        opcion = input("  Selecciona una opción: ")

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
        elif opcion == "0":
            print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
            break

        input(Fore.GREEN + "\n  Presiona Enter para continuar..." + Style.RESET_ALL)

if __name__ == "__main__":
    main()