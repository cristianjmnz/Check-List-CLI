# ✅ Check List CLI

Gestor de tareas en línea de comandos hecho con Python. Ligero, rápido y sin dependencias pesadas — todo desde la terminal.


---

## 📸 Vista previa

```
╔══════════════════════╗
║      CHECK LIST      ║
╚══════════════════════╝
1. Añadir tarea
2. Listar tareas
3. Buscar tarea
4. Marcar tarea como completada
5. Editar tarea
6. Eliminar tarea
7. Gestionar tags
0. Salir
```

---

## ✨ Características

- **Añadir tareas** — guarda nuevas tareas al instante
- **Listar tareas** — muestra solo las pendientes con indicadores visuales
- **Buscar tareas** — filtra por texto en tiempo real
- **Marcar como completada** — marca tareas terminadas sin eliminarlas
- **Editar tareas** — modifica el texto de cualquier tarea pendiente
- **Eliminar tareas** — elimina una o varias tareas a la vez con confirmación
- **Gestionar tags** — ver, crea y elimina tags 
- **Persistencia** — las tareas se guardan en un archivo JSON local
- **Interfaz con colores** — gracias a `colorama`

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
cd Check_List

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
Check_List/
├── main.py             # Punto de entrada del programa
├── tareas.json         # Generado automáticamente al añadir tareas
├── tags.json           # Generado automáticamente al crear el 1º tag
├── requirements.txt    # Dependencias del proyecto
├── .gitignore
└── README.md
```

---

## 🛠️ Tecnologías

- **Python 3** — lenguaje principal
- **JSON** — almacenamiento local de tareas
- **colorama** — colores en la terminal multiplataforma

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

Hecho por [cristianjmnz](https://github.com/cristianjmnz) — proyecto personal de aprendizaje.
