def mostrar_menu():
    print("\n==== CHECK LIST ====")
    print("1. Añadir tarea")
    print("2. Listar tareas")
    print("3. Salir")

def añadir_tarea(tareas):
    texto = input("\nEscribe la tarea: ")
    tareas.append({"texto":texto, "completada":False})

def main():
    tareas = []

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            añadir_tarea(tareas)

        elif opcion == "3":
            break

if __name__ == "__main__":
    main()
