import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os

FILE = "tareas.json"

from colorama import init, Fore, Style
init()

from datetime import datetime

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

def añadir_tarea(tareas):
    texto = input("\nEscribe la tarea: ").strip()
    if not texto:
        print("No puedes añadir una tarea vacía.")
        return

    tareas.append({"texto":texto, "completada":False, "fecha":datetime.now().isoformat()})
    guardar_tareas(tareas)

def listar_tareas(tareas):
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
        print(f"{contador:>2} | {estado} {t['texto']:<30} {tiempo}")

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

def eliminar_tarea(tareas):
    if not tareas:
        print("\nNo hay tareas para eliminar.")
        return

    listar_tareas(tareas)
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

def editar_tarea(tareas):
    if not tareas:
        print("\nNo hay tareas para editar.")
        return

    listar_tareas(tareas)
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

    while True:
        limpiar_pantalla()

        pendientes = sum(1 for t in tareas if not t["completada"])
        print(Fore.CYAN + f"\n📋 Tienes {pendientes} tarea(s) pendiente(s)." + Style.RESET_ALL)

        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            añadir_tarea(tareas)

        elif opcion == "2":
            listar_tareas(tareas)
        
        elif opcion == "3":
            buscar_tarea(tareas)


        elif opcion == "4":
            marcar_completada(tareas)

        elif opcion == "5":
            editar_tarea(tareas)
            guardar_tareas(tareas)

        elif opcion == "6":
            eliminar_tarea(tareas)

        elif opcion == "0":
            break

        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()