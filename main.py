import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os

FILE = "tareas.json"
FILE_TAGS = "tags.json"

from colorama import init, Fore, Style
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
        print("\n-- Gestionar tags --")
        print(Fore.YELLOW + "1." + Style.RESET_ALL + " Ver tags")
        print(Fore.YELLOW + "2." + Style.RESET_ALL + " Crear tag")
        print(Fore.YELLOW + "3." + Style.RESET_ALL + " Eliminar tag")
        print(Fore.YELLOW + "0." + Style.RESET_ALL + " Volver")

        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            if not tags:
                print("No hay tags creados.")
            else:
                for nombre, color in tags.items():
                    print(COLORES_DISPONIBLES[color] + f"● {nombre}" + Style.RESET_ALL)

        elif opcion == "2":
            nombre = input("Nombre del tag: ").strip().lower()
            if not nombre:
                print("El nombre no puede estar vacío.")
                continue
            if nombre in tags:
                print(Fore.RED + "Ya existe un tag con ese nombre." + Style.RESET_ALL)
                continue

            print("Colores disponibles: " + ", ".join(COLORES_DISPONIBLES.keys()))
            color = input("Color: ").strip().lower()
            if color not in COLORES_DISPONIBLES:
                print(Fore.RED + "Color no válido." + Style.RESET_ALL)
                continue

            tags[nombre] = color
            guardar_tags(tags)
            print(COLORES_DISPONIBLES[color] + f"✔ Tag '{nombre}' creado." + Style.RESET_ALL)

        elif opcion == "3":
            if not tags:
                print("No hay tags para eliminar.")
                continue

            for nombre, color in tags.items():
                print(COLORES_DISPONIBLES[color] + f"● {nombre}" + Style.RESET_ALL)

            nombre = input("Nombre del tag a eliminar: ").strip().lower()
            if nombre not in tags:
                print(Fore.RED + "Ese tag no existe." + Style.RESET_ALL)
                continue

            del tags[nombre]
            guardar_tags(tags)
            print(Fore.GREEN + f"✔ Tag '{nombre}' eliminado." + Style.RESET_ALL)

        elif opcion == "0":
            break

def mostrar_menu():
    print(Fore.GREEN + "\n╔══════════════════════╗" + Style.RESET_ALL)
    print(Fore.GREEN + "║      CHECK LIST      ║" + Style.RESET_ALL)
    print(Fore.GREEN + "╚══════════════════════╝" + Style.RESET_ALL)
    print(Fore.YELLOW + "1." + Style.RESET_ALL + " Añadir tarea")
    print(Fore.YELLOW + "2." + Style.RESET_ALL + " Listar tareas")
    print(Fore.YELLOW + "3." + Style.RESET_ALL + " Buscar tarea")
    print(Fore.YELLOW + "4." + Style.RESET_ALL + " Marcar tarea como completada")
    print(Fore.YELLOW + "5." + Style.RESET_ALL + " Editar tarea")
    print(Fore.YELLOW + "6." + Style.RESET_ALL + " Eliminar tarea")
    print(Fore.YELLOW + "7." + Style.RESET_ALL + " Gestionar tags")
    print(Fore.YELLOW + "0." + Style.RESET_ALL + " Salir")

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
        return f"Hace {meses} mes{'s' if meses > 1 else ''}"

def añadir_tarea(tareas, tags):
    texto = input("\nEscribe la tarea: ").strip()
    if not texto:
        print("No puedes añadir una tarea vacía.")
        return

    tag = None
    if tags:
        print("Tags disponibles: ", end="")
        for nombre, color in tags.items():
            print(COLORES_DISPONIBLES[color] + nombre + Style.RESET_ALL, end="  ")
        print()
        entrada = input("Tag (Enter para ninguno): ").strip().lower()
        if entrada and entrada in tags:
            tag = entrada
        elif entrada:
            print(Fore.RED + "Tag no reconocido, se guardará sin tag." + Style.RESET_ALL)

    tareas.append({
        "texto": texto,
        "completada": False,
        "fecha": datetime.now().isoformat(),
        "tag": tag
    })
    guardar_tareas(tareas)

def listar_tareas(tareas, tags):
    if not tareas:
        print("\nNo hay tareas")
        return

    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.GREEN + "\nTodas las tareas están completadas. ¡Buen trabajo!" + Style.RESET_ALL)
        return

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

        print(f"{contador:>2} | {estado} {t['texto']:<30} {tiempo} {tag_str}")

def cargar_tareas():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_tareas(tareas):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=4, ensure_ascii=False)

def marcar_completada(tareas):
    listar_tareas(tareas)
    pendientes = obtener_pendientes_ordenados(tareas)

    try:
        idx = int(input("\nNúmero de tarea: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "Número fuera de rango" + Style.RESET_ALL)
            return

        indice_real, _ = pendientes[idx - 1]
        tareas[indice_real - 1]["completada"] = True
        guardar_tareas(tareas)

    except ValueError:
        print("Número no válido")

def eliminar_tarea(tareas, tags):
    if not tareas:
        print("\nNo hay tareas para eliminar.")
        return

    listar_tareas(tareas, tags)
    pendientes = obtener_pendientes_ordenados(tareas)

    entrada = input("\nSelecciona tareas a eliminar (ej: 1 3 5): ").split()

    try:
        numeros = [int(n) for n in entrada]
    except ValueError:
        print("Debes introducir solo números.")
        return

    confirmacion = input("¿Seguro que quieres eliminar estas tareas? (s/n): ").lower()
    if confirmacion != "s":
        print("Operación cancelada.")
        return

    # Ordenar en reversa por índice real para no desplazar posiciones al borrar
    indices_a_borrar = sorted(
        [pendientes[n - 1][0] for n in numeros if 1 <= n <= len(pendientes)],
        reverse=True
    )

    for indice_real in indices_a_borrar:
        tareas.pop(indice_real - 1)

    guardar_tareas(tareas)
    print(Fore.GREEN + "✔ Tareas eliminadas." + Style.RESET_ALL)

def editar_tarea(tareas, tags):
    if not tareas:
        print("\nNo hay tareas para editar.")
        return

    listar_tareas(tareas, tags)
    pendientes = obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.RED + "No hay tareas pendientes para editar." + Style.RESET_ALL)
        return

    try:
        idx = int(input("\nNúmero de tarea a editar: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "Número fuera de rango." + Style.RESET_ALL)
            return

        indice_real, tarea = pendientes[idx - 1]
        print(f"Texto actual: {tarea['texto']}")
        nuevo_texto = input("Nuevo texto: ").strip()

        if not nuevo_texto:
            print("No puedes dejar la tarea vacía.")
            return

        tareas[indice_real - 1]["texto"] = nuevo_texto
        guardar_tareas(tareas)
        print("✏️  Tarea actualizada.")

    except ValueError:
        print("Debes introducir un número válido.")

def buscar_tarea(tareas):
    palabra = input("¿Qué tarea buscas?: ").strip().lower()

    if not palabra:
        print("Tienes que escribir minimo una letra.")
        return
    
    if not tareas:
        print("\nNo hay tareas guardadas.")
        return
    
    encontrado = False

    for i, t in enumerate(tareas, 1):
        if palabra in t["texto"].lower():
            estado = "✔" if t["completada"] else "✖"
            print(f"{i}.[{estado}]{t['texto']}")
            encontrado = True
    if not encontrado:
        print("No se encontraron tareas con esa palabra.")

def obtener_pendientes_ordenados(tareas):
    pendientes = [(i, t) for i, t in enumerate(tareas, 1) if not t["completada"]]
    pendientes.sort(key=lambda x: x[1].get("fecha", ""), reverse=True)
    return pendientes

def main():
    tareas = cargar_tareas()
    tags   = cargar_tags()       # ← añade esto

    while True:
        limpiar_pantalla()
        pendientes = sum(1 for t in tareas if not t["completada"])
        print(Fore.CYAN + f"\n📋 Tienes {pendientes} tarea(s) pendiente(s)." + Style.RESET_ALL)
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            añadir_tarea(tareas, tags)      # ← pasa tags
        elif opcion == "2":
            listar_tareas(tareas, tags)     # ← pasa tags
        elif opcion == "3":
            buscar_tarea(tareas)
        elif opcion == "4":
            marcar_completada(tareas)
        elif opcion == "5":
            editar_tarea(tareas, tags)
        elif opcion == "6":
            eliminar_tarea(tareas, tags)
        elif opcion == "7":
            gestionar_tags(tags)            # ← opción nueva
        elif opcion == "0":
            break

        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()