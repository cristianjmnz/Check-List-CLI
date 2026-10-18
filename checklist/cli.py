"""Punto de entrada: subcomandos de línea de comandos y arranque del menú."""

import argparse
import sqlite3
import sys

from colorama import Fore, Style

from . import models, notify, paths, storage, ui


def _reconfigurar_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _cmd_add(args):
    tareas = storage.cargar_tareas()
    tags = storage.cargar_tags()

    tag = None
    if args.tag:
        if args.tag in tags:
            tag = args.tag
        else:
            print(
                Fore.RED
                + f"  Tag no reconocido: {args.tag}. Se guardará sin tag."
                + Style.RESET_ALL
            )

    tareas.append(models.crear_tarea(args.texto, tag, args.prioridad))
    storage.guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tarea añadida." + Style.RESET_ALL)


def _cmd_reminder(args):
    if args.hora:
        hora = models.normalizar_hora(args.hora)
        if not hora:
            print(
                Fore.RED
                + f"  Hora no válida: {args.hora}. Usa el formato HH:MM (ej. 08:30)."
                + Style.RESET_ALL
            )
            return 1
        config = storage.cargar_config()
        config["recordatorio_hora"] = hora
        storage.guardar_config(config)
        print(
            Fore.GREEN
            + f"  ✔ Recordatorio configurado a las {hora} (macOS)."
            + Style.RESET_ALL
        )
        return 0

    print(f"  Recordatorio diario: {notify.hora_recordatorio()} (macOS)")
    return 0


def _cmd_list(args):
    tareas = storage.cargar_tareas()
    tags = storage.cargar_tags()
    pendientes = models.obtener_pendientes_ordenados(tareas)

    if not pendientes:
        print("No hay tareas pendientes.")
    else:
        for contador, (_, t) in enumerate(pendientes, 1):
            ui._imprimir_tarea(contador, t, tags)

    if args.all:
        completadas = [t for t in tareas if t.get("completada")]
        if completadas:
            print(Fore.GREEN + "\nCompletadas:" + Style.RESET_ALL)
            for t in completadas:
                print(f"  ✔ {t['texto']}")


def _cmd_done(args):
    tareas = storage.cargar_tareas()
    indice_real = models.indice_real_de_pendiente(tareas, args.numero)
    if indice_real is None:
        print(Fore.RED + "  Número fuera de rango." + Style.RESET_ALL)
        return 1
    tareas[indice_real - 1]["completada"] = True
    storage.guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tarea completada." + Style.RESET_ALL)
    return 0


def _cmd_rm(args):
    tareas = storage.cargar_tareas()
    indice_real = models.indice_real_de_pendiente(tareas, args.numero)
    if indice_real is None:
        print(Fore.RED + "  Número fuera de rango." + Style.RESET_ALL)
        return 1
    tareas.pop(indice_real - 1)
    storage.guardar_tareas(tareas)
    print(Fore.GREEN + "  ✔ Tarea eliminada." + Style.RESET_ALL)
    return 0


def _cmd_notify(args):
    tareas = storage.cargar_tareas()
    return 0 if notify.enviar_pendientes(tareas) else 1


def _cmd_topic(args):
    if args.set is not None:
        tema = args.set.strip()
        if not tema:
            print(
                Fore.RED + "  El tema no puede estar vacío." + Style.RESET_ALL
            )
            return 1
        config = storage.cargar_config()
        config["ntfy_topic"] = tema
        config.setdefault("ntfy_server", paths.NTFY_SERVER_DEFAULT)
        storage.guardar_config(config)
        print(Fore.GREEN + f"✔ Tema ntfy guardado: {tema}" + Style.RESET_ALL)
        return 0

    topic, server = notify.obtener_ntfy()
    if topic:
        print(f"Tema: {topic}")
        print(f"Servidor: {server}")
    else:
        print("No hay tema ntfy configurado.")
    return 0


def _construir_parser():
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

    sub = parser.add_subparsers(dest="comando")

    p_add = sub.add_parser("add", help="Añade una tarea.")
    p_add.add_argument("texto", help="Texto de la tarea.")
    p_add.add_argument("-t", "--tag", help="Tag de la tarea.")
    p_add.add_argument(
        "-p",
        "--prioridad",
        choices=models.PRIORIDADES,
        default="media",
        help="Prioridad de la tarea (alta/media/baja).",
    )
    p_add.set_defaults(func=_cmd_add)

    p_list = sub.add_parser("list", help="Lista las tareas pendientes.")
    p_list.add_argument(
        "--all", action="store_true", help="Incluye también las completadas."
    )
    p_list.set_defaults(func=_cmd_list)

    p_done = sub.add_parser("done", help="Marca una tarea pendiente como completada.")
    p_done.add_argument("numero", type=int, help="Número de la tarea en la lista.")
    p_done.set_defaults(func=_cmd_done)

    p_rm = sub.add_parser("rm", help="Elimina una tarea pendiente.")
    p_rm.add_argument("numero", type=int, help="Número de la tarea en la lista.")
    p_rm.set_defaults(func=_cmd_rm)

    p_notify = sub.add_parser("notify", help="Envía las tareas pendientes por ntfy.")
    p_notify.set_defaults(func=_cmd_notify)

    p_topic = sub.add_parser("topic", help="Muestra o fija el tema ntfy.")
    p_topic.add_argument("--set", metavar="TEMA", help="Fija el tema ntfy.")
    p_topic.set_defaults(func=_cmd_topic)

    p_reminder = sub.add_parser(
        "reminder", help="Muestra o fija la hora del recordatorio diario (macOS)."
    )
    p_reminder.add_argument(
        "hora",
        nargs="?",
        metavar="HH:MM",
        help="Hora del recordatorio (ej. 08:30). Sin argumento la muestra.",
    )
    p_reminder.set_defaults(func=_cmd_reminder)

    return parser


def main(argv=None):
    _reconfigurar_stdout()
    parser = _construir_parser()
    args = parser.parse_args(argv)

    try:
        if args.set_topic is not None:
            return _cmd_topic(argparse.Namespace(set=args.set_topic))

        if args.notify_pendientes:
            return _cmd_notify(args)

        if getattr(args, "func", None) is not None:
            codigo = args.func(args)
            return 0 if codigo is None else codigo

        ui.menu_interactivo()
        return 0
    except sqlite3.Error as exc:
        print(
            Fore.RED
            + f"  Error al acceder a la base de datos: {exc}"
            + Style.RESET_ALL
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
