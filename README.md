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
tareas pendientes (o `Todo al día 🎉` si no tienes ninguna).

### 4. Recordatorio automático diario (macOS)
En `8. Notificaciones` → `3. Instalar recordatorio diario (8:00)` se crea un
agente de `launchd` que envía el resumen cada día a las 8:00, aunque cierres el
programa. Para quitarlo:

```bash
launchctl unload ~/Library/LaunchAgents/com.cristianjmnz.checklist.plist
rm ~/Library/LaunchAgents/com.cristianjmnz.checklist.plist
```

En Linux puedes usar `cron`:

```bash
0 8 * * * /ruta/al/venv/bin/python /ruta/a/main.py --notify-pendientes
```

### Uso desde la línea de comandos

```bash
python main.py --set-topic MI_TEMA       # guarda el tema sin entrar al menú
python main.py --notify-pendientes       # envía los pendientes y sale
```

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
```

Instálalas con:

```bash
pip install -r requirements.txt
```

---

## 📁 Estructura del proyecto

```
Check-List-CLI/
├── main.py             # Punto de entrada del programa
├── tareas.json         # Generado automáticamente al añadir tareas
├── tags.json           # Generado automáticamente al crear el 1º tag
├── config.json         # Generado al configurar ntfy (no se sube al repo)
├── requirements.txt    # Dependencias del proyecto
├── .gitignore
└── README.md
```

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
