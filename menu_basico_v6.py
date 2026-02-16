import json
import os

FILE = "tareas.json"


def mostrar_menu():
    print("\n==== CHECK LIST ====")
    print("1. Añadir tarea")
    print("2. Listar tareas")
    print("3. Marcar tarea como completada")
    print("4. Eliminar tarea")
    print("5. Salir")

def añadir_tarea(tareas):
    texto = input("\nEscribe la tarea: ").strip()
    if not texto:
        print("No puedes añadir una tarea vacía.")

    tareas.append({"texto":texto, "completada":False})
    guardar_tareas(tareas)

def listar_tareas(tareas):
    if not tareas:
        print("\nNo hay tareas")
        return
    
    for i, t in enumerate(tareas, 1):
        estado = "✔" if t["completada"] else "✖"
        print(f"{i}.[{estado}] {t['texto']}")

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
    try:
        idx = int(input("\nNúmero de tarea: "))
        if idx < 1 or idx > len(tareas):
            print("Numero fuera de rango")
            return

        if tareas[idx - 1]["completada"]:
            print("⚠ Esa tarea ya está completada.")
            return

        tareas[idx - 1]["completada"] = True
        guardar_tareas(tareas)
    except ValueError:
        print("Numero no valido")

def eliminar_tarea(tareas):
    if not tareas:
        print("\nNo hay tareas para eliminar.")
        return
    listar_tareas(tareas)
    try:
        idx = int(input("\nSelecciona la tarea que desea eliminar: "))
        if idx < 1 or idx > len(tareas):
            print("Número fuera de rango.")
            return
        tarea_eliminada = tareas.pop(idx -1)
        guardar_tareas(tareas)
        print(f"Tarea eliminada: '{tarea_eliminada['texto']}'")
    except ValueError:
        print("Debes introducir un número válido.")


def main():
    tareas = cargar_tareas()

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            añadir_tarea(tareas)

        elif opcion == "2":
            listar_tareas(tareas)

        elif opcion == "3":
            marcar_completada(tareas)

        elif opcion == "4":
            eliminar_tarea(tareas)

        elif opcion == "5":
            break

if __name__ == "__main__":
    main()
