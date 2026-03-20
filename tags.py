import sqlite3
from colorama import Fore, Style
from database import get_connection

from config import COLORES_DISPONIBLES

# CREATE
def crear_tag(nombre, color):
    if color not in COLORES_DISPONIBLES:
        print(Fore.RED + "Color no válido." + Style.RESET_ALL)
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO tags (nombre, color) VALUES (?, ?)",
            (nombre, color)
        )
        conn.commit()
        print(COLORES_DISPONIBLES[color] + f"✔ Tag '{nombre}' creado." + Style.RESET_ALL)
        return True
    except sqlite3.IntegrityError:
        print(Fore.RED + f"Ya existe un tag con el nombre '{nombre}'." + Style.RESET_ALL)
        return False
    finally:
        conn.close()

# READ
def obtener_tags():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, color FROM tags")
    tags = cursor.fetchall()

    conn.close()
    return tags

def mostrar_tags():
    tags = obtener_tags()

    if not tags:
        print("No hay tags creados.")
        return

    for _, nombre, color in tags:
        print(COLORES_DISPONIBLES[color] + f"● {nombre}" + Style.RESET_ALL)

def obtener_tag_por_nombre(nombre):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, color FROM tags WHERE nombre = ?", (nombre,))
    tag = cursor.fetchone()

    conn.close()
    return tag  # devuelve (id, nombre, color) o None si no existe

# DELETE
def eliminar_tag(nombre):
    tag = obtener_tag_por_nombre(nombre)

    if not tag:
        print(Fore.RED + f"El tag '{nombre}' no existe." + Style.RESET_ALL)
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM tags WHERE nombre = ?", (nombre,))
        conn.commit()
        print(Fore.GREEN + f"✔ Tag '{nombre}' eliminado." + Style.RESET_ALL)
        return True
    except sqlite3.IntegrityError:
        print(Fore.RED + f"No puedes eliminar '{nombre}' porque hay tareas que lo usan." + Style.RESET_ALL)
        print(Fore.YELLOW + "Edita esas tareas primero y quítales el tag." + Style.RESET_ALL)
        return False
    finally:
        conn.close()