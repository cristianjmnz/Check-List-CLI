def mostrar_menu():
    print("\n==== CHECK LIST ====")
    print("1. Añadir tarea")
    print("2. Listar tareas")
    print("3. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción aún no implementada.")

