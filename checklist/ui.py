"""Interfaz interactiva de terminal (menús, prompts y salida con color)."""

import os
import sqlite3

from colorama import Fore, Style

from . import models, notify, paths, storage

COLORES_DISPONIBLES = paths.COLORES_DISPONIBLES

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
            print(
                Fore.CYAN
                + line
                + "   "
                + Style.RESET_ALL
                + Fore.GREEN
                + Style.BRIGHT
                + GITHUB_URL
                + Style.RESET_ALL
            )
        elif i == 2:
            print(
                Fore.CYAN
                + line
                + "   "
                + Style.RESET_ALL
                + Fore.WHITE
                + "Deep clean your task list."
                + Style.RESET_ALL
            )
        else:
            print(Fore.CYAN + line + Style.RESET_ALL)
    print()


def mostrar_barra_atajos():
    atajos = [
        ("1-8", "Seleccionar"),
        ("0", "Salir"),
        ("Enter", "Confirmar"),
    ]
    partes = "   ".join(
        Fore.GREEN
        + Style.BRIGHT
        + f"[{k}]"
        + Style.RESET_ALL
        + Fore.WHITE
        + f" {v}"
        + Style.RESET_ALL
        for k, v in atajos
    )
    print(Fore.GREEN + "  " + "─" * 40 + Style.RESET_ALL)
    print("  " + partes)


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
            "  "
            + Fore.CYAN
            + Style.BRIGHT
            + num
            + Style.RESET_ALL
            + separador
            + "  "
            + Fore.WHITE
            + texto
            + Style.RESET_ALL
        )

    print(Fore.GREEN + "  " + "─" * 36 + Style.RESET_ALL)
    mostrar_barra_atajos()


def limpiar_pantalla():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


# ─── Tags ─────────────────────────────────────────────────────────────────────


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
                    print(
                        "  "
                        + COLORES_DISPONIBLES[color]
                        + f"● {nombre}"
                        + Style.RESET_ALL
                    )

        elif opcion == "2":
            nombre = input("  Nombre del tag: ").strip().lower()
            if not nombre:
                print("  El nombre no puede estar vacío.")
                continue
            if nombre in tags:
                print(Fore.RED + "  Ya existe un tag con ese nombre." + Style.RESET_ALL)
                continue

            print(
                "  Colores disponibles: " + ", ".join(COLORES_DISPONIBLES.keys())
            )
            color = input("  Color: ").strip().lower()
            if color not in COLORES_DISPONIBLES:
                print(Fore.RED + "  Color no válido." + Style.RESET_ALL)
                continue

            tags[nombre] = color
            storage.guardar_tags(tags)
            print(
                COLORES_DISPONIBLES[color]
                + f"  ✔ Tag '{nombre}' creado."
                + Style.RESET_ALL
            )

        elif opcion == "3":
            if not tags:
                print("  No hay tags para eliminar.")
                continue

            for nombre, color in tags.items():
                print(
                    "  "
                    + COLORES_DISPONIBLES[color]
                    + f"● {nombre}"
                    + Style.RESET_ALL
                )

            nombre = input("  Nombre del tag a eliminar: ").strip().lower()
            if nombre not in tags:
                print(Fore.RED + "  Ese tag no existe." + Style.RESET_ALL)
                continue

            del tags[nombre]
            storage.guardar_tags(tags)
            print(Fore.GREEN + f"  ✔ Tag '{nombre}' eliminado." + Style.RESET_ALL)

        elif opcion == "0":
            break


# ─── Tareas ───────────────────────────────────────────────────────────────────


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
            print(
                Fore.RED
                + "  Tag no reconocido, se guardará sin tag."
                + Style.RESET_ALL
            )

    prioridad = (
        input("  Prioridad (alta/media/baja, Enter = media): ").strip().lower()
    )
    tareas.append(models.crear_tarea(texto, tag, prioridad))
    storage.guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tarea añadida." + Style.RESET_ALL)


_MARCA_PRIORIDAD = {"alta": Fore.RED + "[!] " + Style.RESET_ALL}


def _imprimir_tarea(contador, t, tags):
    estado = Fore.YELLOW + "○" + Style.RESET_ALL

    if t.get("fecha"):
        tiempo = Fore.CYAN + f"({models.tiempo_relativo(t['fecha'])})" + Style.RESET_ALL
    else:
        tiempo = Fore.CYAN + "(Sin fecha)" + Style.RESET_ALL

    tag_str = ""
    if t.get("tag") and t["tag"] in tags:
        color = COLORES_DISPONIBLES.get(tags[t["tag"]], "")
        tag_str = color + f"[{t['tag']}]" + Style.RESET_ALL

    marca = _MARCA_PRIORIDAD.get(t.get("prioridad"), "")
    print(f"  {contador:>2} | {estado} {marca}{t['texto']:<30} {tiempo} {tag_str}")


def listar_tareas(tareas, tags):
    if not tareas:
        print("\n  No hay tareas")
        return

    pendientes = models.obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(
            Fore.GREEN
            + "\n  Todas las tareas están completadas. ¡Buen trabajo!"
            + Style.RESET_ALL
        )
        return

    print()
    for contador, (_, t) in enumerate(pendientes, 1):
        _imprimir_tarea(contador, t, tags)


def marcar_completada(tareas, tags):
    pendientes = models.obtener_pendientes_ordenados(tareas)
    if not pendientes:
        print("\n  No hay tareas pendientes para marcar como completadas.")
        return

    listar_tareas(tareas, tags)

    try:
        idx = int(input("\n  Número de tarea: "))
        indice_real = models.indice_real_de_pendiente(tareas, idx)
        if indice_real is None:
            print(Fore.RED + "  Número fuera de rango" + Style.RESET_ALL)
            return

        tareas[indice_real - 1]["completada"] = True
        storage.guardar_tareas(tareas)
        print(Fore.GREEN + "  ✔ Tarea completada." + Style.RESET_ALL)

    except ValueError:
        print("  Número no válido")


def eliminar_tarea(tareas, tags):
    if not tareas:
        print("\n  No hay tareas para eliminar.")
        return

    pendientes = models.obtener_pendientes_ordenados(tareas)
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
        indice_real = models.indice_real_de_pendiente(tareas, n)
        if indice_real is not None and indice_real not in indices_validos:
            indices_validos.append(indice_real)

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

    storage.guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tareas eliminadas." + Style.RESET_ALL)


def editar_tarea(tareas, tags):
    if not tareas:
        print("\n  No hay tareas para editar.")
        return

    pendientes = models.obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print(Fore.RED + "  No hay tareas pendientes para editar." + Style.RESET_ALL)
        return

    listar_tareas(tareas, tags)

    try:
        idx = int(input("\n  Número de tarea a editar: "))
        indice_real = models.indice_real_de_pendiente(tareas, idx)
        if indice_real is None:
            print(Fore.RED + "  Número fuera de rango." + Style.RESET_ALL)
            return

        tarea = tareas[indice_real - 1]
        print(f"  Texto actual: {tarea['texto']}")
        nuevo_texto = input("  Nuevo texto (Enter para mantener): ").strip()

        if nuevo_texto:
            tarea["texto"] = nuevo_texto

        if tags:
            print("  Tags disponibles: ", end="")
            for nombre, color in tags.items():
                print(COLORES_DISPONIBLES[color] + nombre + Style.RESET_ALL, end="  ")
            print()
            entrada = (
                input("  Nuevo tag (Enter para mantener, '-' para quitar): ")
                .strip()
                .lower()
            )
            if entrada == "-":
                tarea["tag"] = None
            elif entrada and entrada in tags:
                tarea["tag"] = entrada
            elif entrada:
                print(
                    Fore.RED
                    + "  Tag no reconocido, se mantiene el tag actual."
                    + Style.RESET_ALL
                )

        prioridad = (
            input("  Nueva prioridad (Enter para mantener): ").strip().lower()
        )
        if prioridad in models.PRIORIDADES:
            tarea["prioridad"] = prioridad

        storage.guardar_tareas(tareas)
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

    numeros = {
        real: mostrado
        for mostrado, (real, _) in enumerate(
            models.obtener_pendientes_ordenados(tareas), 1
        )
    }

    encontrado = False

    for real, t in enumerate(tareas, 1):
        if palabra not in t["texto"].lower():
            continue
        encontrado = True
        if t["completada"]:
            estado = Fore.GREEN + "✔" + Style.RESET_ALL
            print(f"   ✔ [{estado}] {t['texto']}")
        else:
            estado = Fore.YELLOW + "○" + Style.RESET_ALL
            print(f"  {numeros[real]:>2} [{estado}] {t['texto']}")

    if not encontrado:
        print(
            Fore.RED
            + "  No se encontraron tareas con esa palabra."
            + Style.RESET_ALL
        )


# ─── Notificaciones (UI) ──────────────────────────────────────────────────────


def mostrar_instrucciones_ntfy(topic, server=None):
    server = (server or paths.NTFY_SERVER_DEFAULT).rstrip("/")
    print()
    print(
        Fore.CYAN
        + "  Instala la app 'ntfy' en tu móvil (App Store / Play Store / F-Droid)."
        + Style.RESET_ALL
    )
    print(Fore.CYAN + "  Suscríbete a este tema:" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + f"      {topic}" + Style.RESET_ALL)
    print(Fore.CYAN + "  O abre directamente:" + Style.RESET_ALL)
    print(Fore.WHITE + f"      {server}/{topic}" + Style.RESET_ALL)


def configurar_tema():
    topic, server = notify.obtener_ntfy()
    config = storage.cargar_config()
    if "ntfy_server" not in config:
        config["ntfy_server"] = server

    if topic:
        print(f"  Tema actual: {Fore.CYAN}{topic}{Style.RESET_ALL}")
        respuesta = input("  ¿Generar uno nuevo? (s/n): ").strip().lower()
        if respuesta != "s":
            mostrar_instrucciones_ntfy(topic, server)
            return

    nuevo = notify.generar_tema()
    config["ntfy_topic"] = nuevo
    storage.guardar_config(config)
    print(Fore.GREEN + f"\n  ✔ Tema generado: {nuevo}" + Style.RESET_ALL)
    mostrar_instrucciones_ntfy(nuevo, server)


def gestionar_notificaciones(tareas, tags):
    while True:
        print(Fore.GREEN + "\n  ── Notificaciones ──" + Style.RESET_ALL)
        print("  " + Fore.CYAN + "1." + Style.RESET_ALL + " Configurar tema")
        print(
            "  "
            + Fore.CYAN
            + "2."
            + Style.RESET_ALL
            + " Enviar pendientes al móvil"
        )
        print(
            "  "
            + Fore.CYAN
            + "3."
            + Style.RESET_ALL
            + " Instalar recordatorio diario"
        )
        print(
            "  "
            + Fore.CYAN
            + "4."
            + Style.RESET_ALL
            + f" Hora del recordatorio ({notify.hora_recordatorio()})"
        )
        print("  " + Fore.CYAN + "0." + Style.RESET_ALL + " Volver")

        opcion = input("\n  Selecciona una opción: ").strip()

        if opcion == "1":
            configurar_tema()
        elif opcion == "2":
            if notify.enviar_pendientes(tareas):
                print(Fore.GREEN + "  ✔ Notificación enviada." + Style.RESET_ALL)
        elif opcion == "3":
            notify.instalar_recordatorio()
        elif opcion == "4":
            actual = notify.hora_recordatorio()
            entrada = input(f"  Nueva hora HH:MM (Enter para mantener {actual}): ").strip()
            if not entrada:
                continue
            hora = models.normalizar_hora(entrada)
            if not hora:
                print(Fore.RED + "  Hora no válida. Usa el formato HH:MM." + Style.RESET_ALL)
                continue
            config = storage.cargar_config()
            config["recordatorio_hora"] = hora
            storage.guardar_config(config)
            print(Fore.GREEN + f"  ✔ Recordatorio a las {hora}." + Style.RESET_ALL)
        elif opcion == "0":
            break


# ─── Main interactivo ─────────────────────────────────────────────────────────


def menu_interactivo():
    try:
        tareas = storage.cargar_tareas()
        tags = storage.cargar_tags()

        while True:
            limpiar_pantalla()
            pendientes = sum(1 for t in tareas if not t.get("completada", False))
            mostrar_menu()
            print(
                Fore.CYAN
                + f"\n  📋 {pendientes} tarea(s) pendiente(s)\n"
                + Style.RESET_ALL
            )
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
                input(
                    Fore.GREEN
                    + "\n  Presiona Enter para continuar..."
                    + Style.RESET_ALL
                )
            except (EOFError, KeyboardInterrupt):
                print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
                break
    except (KeyboardInterrupt, EOFError):
        print(Fore.GREEN + "\n  Hasta luego 👋\n" + Style.RESET_ALL)
    except sqlite3.Error as exc:
        print(
            Fore.RED
            + f"\n  Error al acceder a la base de datos: {exc}"
            + Style.RESET_ALL
        )
