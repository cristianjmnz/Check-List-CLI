from checklist import models


def _tarea(texto, completada=False, fecha=None, tag=None):
    return {
        "texto": texto,
        "completada": completada,
        "fecha": fecha,
        "tag": tag,
        "prioridad": "media",
    }


def test_normalizar_tarea_valores_minimos():
    t = models.normalizar_tarea({"texto": "hola"})
    assert t == {
        "texto": "hola",
        "completada": False,
        "fecha": None,
        "tag": None,
        "prioridad": "media",
    }


def test_normalizar_tarea_convierte_tipos():
    t = models.normalizar_tarea(
        {"texto": 42, "completada": "si", "fecha": 5, "tag": ["no"]}
    )
    assert t["texto"] == "42"
    assert t["completada"] is True
    assert t["fecha"] is None
    assert t["tag"] is None
    assert t["prioridad"] == "media"


def test_normalizar_tarea_prioridad_valida():
    assert models.normalizar_tarea({"texto": "a", "prioridad": "alta"})["prioridad"] == "alta"
    assert models.normalizar_tarea({"texto": "a", "prioridad": "baja"})["prioridad"] == "baja"
    assert models.normalizar_tarea({"texto": "a", "prioridad": "urgente"})["prioridad"] == "media"
    assert models.normalizar_tarea({"texto": "a", "prioridad": 5})["prioridad"] == "media"


def test_normalizar_tarea_no_dict():
    assert models.normalizar_tarea("basura") is None
    assert models.normalizar_tarea(None) is None


def test_normalizar_tags():
    data = {"a": "rojo", "b": "neon", 3: "verde"}
    assert models.normalizar_tags(data, {"rojo"}) == {"a": "rojo"}
    assert models.normalizar_tags("nope", {"rojo"}) == {}


def test_normalizar_config():
    data = {"ntfy_topic": "abc", "ntfy_server": "https://x", "otra": 1, "num": 5}
    assert models.normalizar_config(data) == {
        "ntfy_topic": "abc",
        "ntfy_server": "https://x",
    }


def test_normalizar_config_comandos():
    data = {
        "ntfy_cmd_topic": " cmd-abc ",
        "ntfy_cmd_token": "tok",
        "ntfy_last_id": "abc123",
    }
    assert models.normalizar_config(data) == {
        "ntfy_cmd_topic": "cmd-abc",
        "ntfy_cmd_token": "tok",
        "ntfy_last_id": "abc123",
    }


def test_normalizar_config_descarta_comandos_vacios():
    data = {"ntfy_cmd_topic": "  ", "ntfy_cmd_token": "", "ntfy_last_id": None}
    assert models.normalizar_config(data) == {}


def test_normalizar_config_con_hora_valida():
    assert models.normalizar_config({"recordatorio_hora": "9:05"})["recordatorio_hora"] == "09:05"


def test_normalizar_config_ignora_hora_invalida():
    assert "recordatorio_hora" not in models.normalizar_config({"recordatorio_hora": "25:99"})


def test_normalizar_hora():
    assert models.normalizar_hora("9:05") == "09:05"
    assert models.normalizar_hora("23:59") == "23:59"
    assert models.normalizar_hora(" 08:00 ") == "08:00"
    assert models.normalizar_hora("24:00") is None
    assert models.normalizar_hora("08:60") is None
    assert models.normalizar_hora("ocho") is None
    assert models.normalizar_hora(None) is None


def test_crear_tarea():
    t = models.crear_tarea("comprar", "personal", "alta")
    assert t["texto"] == "comprar"
    assert t["completada"] is False
    assert t["tag"] == "personal"
    assert t["prioridad"] == "alta"
    assert t["fecha"]


def test_crear_tarea_prioridad_por_defecto():
    assert models.crear_tarea("x")["prioridad"] == "media"


def test_prioridad_max():
    pendientes = models.obtener_pendientes_ordenados(
        [
            _tarea("a", fecha="2026-01-01T00:00:00", tag=None),
            _tarea("b", fecha="2026-06-01T00:00:00", tag=None),
        ]
    )
    assert models.prioridad_max(pendientes) == "media"
    assert models.prioridad_max([]) is None


def test_prioridad_max_gana_alta():
    tareas = [
        models.crear_tarea("urgente", prioridad="alta"),
        models.crear_tarea("normal", prioridad="baja"),
    ]
    assert models.prioridad_max(models.obtener_pendientes_ordenados(tareas)) == "alta"


def test_obtener_pendientes_ordenados_mantiene_prioridad():
    t = models.crear_tarea("con prioridad", prioridad="alta")
    (_, pendiente) = models.obtener_pendientes_ordenados([t])[0]
    assert pendiente["prioridad"] == "alta"


def test_obtener_pendientes_ordenados_mas_recientes_primero():
    tareas = [
        _tarea("vieja", fecha="2026-01-01T00:00:00"),
        _tarea("nueva", fecha="2026-06-01T00:00:00"),
        _tarea("hecha", completada=True, fecha="2026-06-02T00:00:00"),
        _tarea("sin_fecha", fecha=None),
    ]
    result = models.obtener_pendientes_ordenados(tareas)
    textos = [t["texto"] for _, t in result]
    assert textos == ["nueva", "vieja", "sin_fecha"]
    assert result[0][0] == 2  # índice real de 'nueva'


def test_indice_real_de_pendiente():
    tareas = [
        _tarea("a", fecha="2026-01-01T00:00:00"),
        _tarea("b", completada=True),
        _tarea("c", fecha="2026-06-01T00:00:00"),
    ]
    # pendientes ordenados: c(real 3), a(real 1)
    assert models.indice_real_de_pendiente(tareas, 1) == 3
    assert models.indice_real_de_pendiente(tareas, 2) == 1
    assert models.indice_real_de_pendiente(tareas, 3) is None
    assert models.indice_real_de_pendiente(tareas, 0) is None


def test_tiempo_relativo_momento():
    assert models.tiempo_relativo("<no-es-fecha>") == "(fecha inválida)"
    assert models.tiempo_relativo("9999-01-01T00:00:00") == "En el futuro"


def test_tiempo_relativo_minutos():
    from datetime import datetime, timedelta

    fecha = (datetime.now() - timedelta(minutes=5)).isoformat()
    assert models.tiempo_relativo(fecha) == "Hace 5 minutos"


def test_tiempo_relativo_horas():
    from datetime import datetime, timedelta

    fecha = (datetime.now() - timedelta(hours=2)).isoformat()
    assert models.tiempo_relativo(fecha) == "Hace 2 horas"


def test_tiempo_relativo_anos():
    from datetime import datetime, timedelta

    fecha = (datetime.now() - timedelta(days=400)).isoformat()
    assert models.tiempo_relativo(fecha) == "Hace 1 año"


def test_tiempo_relativo_con_z():
    from datetime import datetime, timedelta

    fecha = (datetime.now() - timedelta(seconds=30)).isoformat() + "Z"
    assert models.tiempo_relativo(fecha) == "Hace un momento"