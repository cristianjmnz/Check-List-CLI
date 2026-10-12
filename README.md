# ✅ Check List CLI

Gestor de tareas en línea de comandos hecho con Python. Ligero, rápido y sin dependencias pesadas — todo desde la terminal.


---

## 📸 Vista previa

```
1. Añadir tarea
2. Listar tareas
3. Buscar tarea
4. Marcar tarea como completada
5. Editar tarea
6. Eliminar tarea
7. Gestionar tags
8. Notificaciones
0. Salir
```

---

## ✨ Características

- **Añadir tareas** — guarda nuevas tareas al instante
- **Listar tareas** — muestra solo las pendientes con indicadores visuales
- **Buscar tareas** — filtra por texto en tiempo real
- **Marcar como completada** — marca tareas terminadas sin eliminarlas
- **Editar tareas** — modifica el texto y el tag de cualquier tarea pendiente
- **Eliminar tareas** — elimina una o varias tareas a la vez con confirmación
- **Gestionar tags** — ver, crear y eliminar tags
- **Notificaciones ntfy** — recibe tus tareas pendientes en el móvil
- **Persistencia** — las tareas se guardan en un archivo JSON local
- **Interfaz con colores** — gracias a `colorama`

---

## 📲 Notificaciones al móvil (ntfy)

Puedes recibir un resumen de tus tareas pendientes como notificación push usando
[ntfy.sh](https://ntfy.sh) (gratis, sin registro).

### 1. Crea tu tema
En el menú principal entra en `8. Notificaciones` → `1. Configurar tema`. Se
generará un tema aleatorio (por ejemplo `checklist-8f3a91b2`) que actúa como
contraseña: guarda el que se te muestre.

### 2. Suscríbete desde el móvil
1. Instala la app **ntfy**:
   - [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - [App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
   - [F-Droid](https://f-droid.org/en/packages/io.heckel.ntfy/)
2. Pulsa **+ (Subscribe to topic)** y escribe exactamente tu tema (ej. `checklist-8f3a91b2`).
   También puedes abrir `https://ntfy.sh/TU_TEMA` en el navegador para probar.

### 3. Envía una notificación
En `8. Notificaciones` → `2. Enviar pendientes al móvil`. Recibirás la lista de
tareas pendientes (o `Todo al día 🎉` si no tienes ninguna). Las tareas con
prioridad **alta** aparecen marcadas con ⚠ y la notificación llega con prioridad
**high** (salta a pantalla completa en el móvil). La notificación incluye un
botón **Abrir** con el enlace a tu tema.

### Prioridad de las tareas
Cada tarea tiene una prioridad (`alta`, `media` o `baja`):

- En el menú: al añadir o editar se te pregunta la prioridad (Enter = media).
- Por línea de comandos: `python main.py add "Entregar informe" -p alta`.
- En la lista, las tareas **altas** muestran un `[!]` en rojo.

### Recordatorio automático diario (macOS)
En `8. Notificaciones` → `3. Instalar recordatorio diario` se crea un
agente de `launchd` que envía el resumen cada día a la hora configurada
(default `08:00`), aunque cierres el programa. Para cambiar la hora usa
`8. Notificaciones` → `4. Hora del recordatorio`, o por línea de comandos:

```bash
python main.py reminder          # muestra la hora actual
python main.py reminder 09:15    # cambia la hora a las 9:15
```

Para quitar el recordatorio:

```bash
launchctl unload ~/Library/LaunchAgents/com.cristianjmnz.checklist.plist
rm ~/Library/LaunchAgents/com.cristianjmnz.checklist.plist
```

En Linux puedes usar `cron`:

```bash
0 8 * * * /ruta/al/venv/bin/python /ruta/a/main.py --notify-pendientes
```

### Uso desde la línea de comandos

Sin abrir el menú interactivo puedes usar subcomandos:

```bash
python main.py add "Comprar pan"                    # añade una tarea
python main.py add "Estudiar SQL" -t tareas         # añade con tag
python main.py add "Entregar informe" -p alta       # añade con prioridad alta
python main.py list                                 # muestra las pendientes
python main.py list --all                           # incluye las completadas
python main.py done 2                               # marca la pendiente nº 2
python main.py rm 1                                 # elimina la pendiente nº 1
python main.py notify                               # envía los pendientes al móvil
python main.py topic                                # muestra el tema ntfy actual
python main.py topic --set MI_TEMA                  # fija el tema sin entrar al menú
python main.py reminder                             # muestra la hora del recordatorio
python main.py reminder 09:15                       # cambia la hora del recordatorio
```

Compatibilidad con las banderas antiguas (cron / launchd):

```bash
python main.py --set-topic MI_TEMA       # equivalente a: topic --set MI_TEMA
python main.py --notify-pendientes       # equivalente a: notify
```

> 💡 Si instalas el paquete (`pip install -e .`), el mismo comando está disponible como `checklist`:
> `checklist list`, `checklist add "Comprar pan"`, etc.

### Privacidad
El texto de tus tareas se envía a los servidores de ntfy.sh. El tema es el único
secreto: usa uno difícil de adivinar. Si te preocupa la privacidad, puedes
auto-alojar tu propio servidor ntfy y cambiarlo en `config.json` (`ntfy_server`).

---
### ⚠️ macOS — Primer uso

Apple bloqueará la app por no estar firmada. Para solucionarlo:

1. Descarga el archivo `checklist` desde Releases
2. Abre la terminal y ejecuta:

```bash
xattr -d com.apple.quarantine ~/Downloads/checklist
chmod +x ~/Downloads/checklist
```

3. Muévelo para usarlo desde cualquier lugar (opcional):

```bash
sudo cp ~/Downloads/checklist /usr/local/bin/checklist
```

Ya puedes escribir `checklist` en cualquier terminal.


## 🚀 Instalación y uso en Windows

### Opción 1 — Ejecutable directo (recomendado)

Descarga el `.exe` desde la sección [Releases](../../releases) y ejecútalo. No necesitas instalar Python.

### Opción 2 — Desde el código fuente

**Requisitos:** Python 3.8 o superior

```bash
# 1. Clona el repositorio
git clone https://github.com/cristianjmnz/Check-List-CLI.git
cd Check-List-CLI

# 2. Instala las dependencias
pip install -r requirements.txt

# 3. Ejecuta el programa
python main.py
```

---

## 📦 Dependencias

```
colorama
platformdirs
```

Instálalas con:

```bash
pip install -r requirements.txt
```

o desarrolla con el paquete instalado en modo editable:

```bash
pip install -e ".[dev]"
```

---

## 📁 Estructura del proyecto

```
Check-List-CLI/
├── main.py               # Punto de entrada (delgado)
├── checklist/
│   ├── cli.py            # Subcomandos de línea de comandos
│   ├── ui.py             # Menú interactivo y salida con color
│   ├── models.py         # Lógica pura (orden, normalización, tiempo relativo)
│   ├── storage.py        # Persistencia JSON (atómica y con respaldo)
│   ├── notify.py         # Notificaciones ntfy + recordatorio launchd
│   └── paths.py          # Rutas de datos y constantes
├── tests/                # Pruebas (pytest)
├── pyproject.toml        # Metadatos, script `checklist`, config ruff/pytest
├── tareas.json           # Generado automáticamente al añadir tareas
├── tags.json             # Generado automáticamente al crear el 1º tag
├── config.json           # Generado al configurar ntfy (no se sube al repo)
├── requirements.txt      # Dependencias del proyecto
├── .github/workflows/ci.yml  # CI: ruff + pytest (Python 3.9–3.13)
└── .gitignore
```

---

## 🧪 Desarrollo

```bash
# Pruebas
python -m pytest

# Linter
ruff check .
```

La funcionalidad no interactiva (subcomandos) está cubierta por tests; el menú
interactivo se prueba manualmente. Los datos están aislados en las pruebas
(`tmp_path`), nunca se tocan tus `tareas.json`/`config.json` reales.

---

## 🛠️ Tecnologías

- **Python 3** — lenguaje principal
- **JSON** — almacenamiento local de tareas
- **colorama** — colores en la terminal multiplataforma
- **ntfy** — notificaciones push al móvil (vía `urllib` de la stdlib)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

Hecho por [cristianjmnz](https://github.com/cristianjmnz) — proyecto personal de aprendizaje.
