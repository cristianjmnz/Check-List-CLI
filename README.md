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
- **Persistencia** — los datos se guardan en una base de datos SQLite local (`tareas.db`)
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
**high** (salta a pantalla completa en el móvil).

### 4. Completa tareas desde el móvil
El resumen incluye hasta **3 botones** (`✔ Completar 1`, `✔ Completar 2`,
`✔ Completar 3`) para las 3 primeras tareas pendientes. Al pulsarlos se envía un
comando a un tema privado de ntfy; no hace falta abrir la app.

En iOS puede que tengas que **expandir la notificación** (mantener pulsada o
deslizar hacia abajo) para ver los botones. El límite de 3 botones es de ntfy;
las demás tareas se completan desde el menú o con `python main.py done N`.

Los comandos se aplican cuando vuelves a usar el CLI: al abrir el menú, al
ejecutar `list`, `done`, `rm` o `notify`, o al usar `8. Notificaciones` →
`5. Sincronizar completadas desde el móvil`. También puedes forzarlo con:

```bash
python main.py sync
```

Así funciona aunque el Mac estuviera apagado o dormido: ntfy guarda los
comandos y se procesan la próxima vez que arranques el CLI. ntfy.sh conserva
los mensajes unas 12 horas.

> 🔒 El canal de comandos usa un tema y un token aleatorios distintos del tema
> principal. Se guardan en `tareas.db` y se generan automáticamente la primera
> vez que envías un resumen.

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
python main.py sync                                 # aplica completadas desde el móvil
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
auto-alojar tu propio servidor ntfy y cambiarlo con
`python main.py topic --set MI_TEMA` (o editando la tabla `config` de `tareas.db`).

---

## 🚀 Instalación y uso en Windows

**Requisitos:** Python 3.9 o superior

```bash
# 1. Clona el repositorio
git clone https://github.com/cristianjmnz/Check-List-CLI.git
cd Check-List-CLI

# 2. Instala las dependencias
pip install -e .

# 3. Ejecuta el programa
python main.py
```

> 💡 Con el paquete instalado también está disponible el comando `checklist`.

---

## 📦 Dependencias

Declaradas en `pyproject.toml`:
```
colorama
platformdirs
```

Instálalas (modo editable, con herramientas de desarrollo):

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
│   ├── storage.py        # Persistencia SQLite (transacciones y migración)
│   ├── notify.py         # Notificaciones ntfy + recordatorio launchd
│   ├── sync.py           # Aplica completadas enviadas desde el móvil
│   └── paths.py          # Rutas de datos y constantes
├── tests/                # Pruebas (pytest)
├── pyproject.toml        # Metadatos, script `checklist`, config ruff/pytest
├── .github/workflows/ci.yml  # CI: ruff + pytest (Python 3.9–3.13)
└── .gitignore
```

### 💾 Persistencia

Todo se guarda en un único archivo `tareas.db` (SQLite, de la stdlib de Python,
sin dependencias extra). La primera vez, si había `tareas.json`/`tags.json`/
`config.json` en el directorio, se importaron automáticamente a la base y los
JSON ya no se usan.

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
(`tmp_path`), nunca se toca tu `tareas.db` real.

---

## 🛠️ Tecnologías

- **Python 3** — lenguaje principal
- **SQLite** — almacenamiento local de tareas (`sqlite3` de la stdlib)
- **colorama** — colores en la terminal multiplataforma
- **ntfy** — notificaciones push al móvil (vía `urllib` de la stdlib)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

Hecho por [cristianjmnz](https://github.com/cristianjmnz) — proyecto personal de aprendizaje.
