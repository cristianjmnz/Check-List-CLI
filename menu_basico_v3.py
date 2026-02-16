import json
import os

FILE = "tareas.json"


def mostrar_menu():
    print("\n==== CHECK LIST ====")
    print("1. Añadir tarea")
    print("2. Listar tareas")
    print("3. Salir")

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
        print(f"{i}. {t['texto']}")

def cargar_tareas():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_tareas(tareas):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=4, ensure_ascii=False)

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
            break

if __name__ == "__main__":
    main()
