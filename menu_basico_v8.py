import json
import os

FILE = "tareas.json"

from colorama import init, Fore, Style
init()


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

def añadir_tarea(tareas):
    texto = input("\nEscribe la tarea: ").strip()
    if not texto:
        print("No puedes añadir una tarea vacía.")
        return

    tareas.append({"texto":texto, "completada":False})
    guardar_tareas(tareas)

def listar_tareas(tareas):
    if not tareas:
        print("\nNo hay tareas")
        return
    
    contador = 1
    
    for t in tareas:
        if not t["completada"]:
            estado = Fore.YELLOW + "○" + Style.RESET_ALL
            print(f"{contador:>2} | {estado} {t['texto']}")
            contador +=1
        
    if contador == 1:
        print(Fore.GREEN + "\nTodas las tareas están completadas. ¡Buen trabajo!" + Style.RESET_ALL)

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
    pendientes = []
    
    for i, t in enumerate(tareas,1):
        if not t["completada"]:
            pendientes.append((i,t))
    
    try:
        idx = int(input("\nNúmero de tarea: "))
        if idx < 1 or idx > len(pendientes):
            print(Fore.RED + "Número fuera de rango" + Style.RESET_ALL)
            return

        indice_real = pendientes[idx - 1][0]
        tareas[indice_real - 1]["completada"] = True
        guardar_tareas(tareas)

    except ValueError:
        print("Numero no valido")

def eliminar_tarea(tareas):
    if not tareas:
        print("\nNo hay tareas para eliminar.")
        return

    listar_tareas(tareas)

    pendientes = []
    for i, t in enumerate(tareas, 1):
        if not t["completada"]:
            pendientes.append((i, t))

    entrada = input("\nSelecciona tareas a eliminar (ej: 1 3 5): ").split()

    try:
        numeros = [int(n) for n in entrada]
    except ValueError:
        print("Debes introducir solo números.")
        return

    numeros.sort(reverse=True)

    confirmacion = input("¿Seguro que quieres eliminar estas tareas? (s/n): ").lower()
    if confirmacion != "s":
        print("Operación cancelada.")
        return

    for n in numeros:
        if n < 1 or n > len(pendientes):
            print(f"Número fuera de rango: {n}")
            continue

        indice_real = pendientes[n - 1][0]
        tareas.pop(indice_real - 1)

    guardar_tareas(tareas)

    print(Fore.GREEN + "✔ Tareas eliminadas." + Style.RESET_ALL)

def editar_tarea(lista):
    listar_tareas(lista)

    if not lista:
        print("\nNo hay tareas para editar.")
        return
    
    listar_tareas(lista)

    try:
        indice = int(input("Número de la tarea a editar: ")) -1

        if 0 <= indice < len(lista):
            print(f"Texto actual: {lista[indice]['texto']}")
            nuevo_texto = input("Nuevo texto: ").strip()

            if not nuevo_texto:
                print("No puedes dejar la tarea vacía.")
                return

            lista[indice]["texto"] = nuevo_texto
            guardar_tareas(lista)
            print("✏️ Tarea actualizada")
        else:
            print("Ese número no existe.")

    except ValueError:
        print("Debes introducir un número valido")

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