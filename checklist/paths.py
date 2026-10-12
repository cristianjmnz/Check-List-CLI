"""Rutas de datos, colores y constantes globales."""

import sys
from pathlib import Path

from colorama import Fore, init

init()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolver_data_dir():
    if getattr(sys, "frozen", False):
        try:
            from platformdirs import user_data_dir

            return Path(user_data_dir("Check-List-CLI", roaming=False))
        except Exception:
            return Path.home() / ".checklist"
    return PROJECT_ROOT


DATA_DIR = _resolver_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILE = DATA_DIR / "tareas.json"
FILE_TAGS = DATA_DIR / "tags.json"
FILE_CONFIG = DATA_DIR / "config.json"

NTFY_SERVER_DEFAULT = "https://ntfy.sh"
NTFY_LIMITE_BYTES = 3900

COLORES_DISPONIBLES = {
    "rojo": Fore.RED,
    "verde": Fore.GREEN,
    "amarillo": Fore.YELLOW,
    "azul": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "blanco": Fore.WHITE,
}
