import sqlite3

DB_NAME = "tareas.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def creardb():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tareas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto TEXT NOT NULL,
        completada INTEGER DEFAULT 0,
        fecha TEXT,
        tag_id INTEGER,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE RESTRICT
    )
    """)

    conn.commit()
    conn.close()