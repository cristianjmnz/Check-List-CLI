import urllib.request

import pytest

from checklist import models, notify, paths


class _FakeResp:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def sin_topic(monkeypatch):
    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    monkeypatch.delenv("NTFY_SERVER", raising=False)
    monkeypatch.setattr(
        notify.storage, "cargar_config", lambda *a, **k: {"ntfy_server": "https://ntfy.sh"}
    )


@pytest.fixture
def con_topic(monkeypatch, tmp_path):
    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    monkeypatch.delenv("NTFY_SERVER", raising=False)
    monkeypatch.setattr(paths, "DB", tmp_path / "tareas.db")
    notify.storage.guardar_config(
        {"ntfy_topic": "prueba-topic", "ntfy_server": "https://ntfy.sh"}
    )
    return "prueba-topic"


def test_enviar_notificacion_sin_tema_devuelve_false(sin_topic, capsys):
    assert notify.enviar_notificacion("T", "m") is False
    assert "No hay tema" in capsys.readouterr().out


def test_enviar_notificacion_exito(con_topic, monkeypatch, capsys):
    capturado = {}

    def fake_urlopen(req, timeout, context):
        capturado["url"] = req.full_url
        capturado["title"] = req.headers.get("Title")
        capturado["tags"] = req.headers.get("Tags")
        capturado["priority"] = req.headers.get("Priority")
        capturado["actions"] = req.headers.get("Actions")
        capturado["data"] = req.data
        return _FakeResp(200)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert notify.enviar_notificacion("Mi título", "Mensaje", tags="memo") is True
    assert capturado["url"] == "https://ntfy.sh/prueba-topic"
    assert capturado["title"] == "Mi título"
    assert capturado["tags"] == "memo"
    assert capturado["data"] == b"Mensaje"
    assert capturado["priority"] is None


def test_enviar_notificacion_prioridad_y_accion(con_topic, monkeypatch):
    capturado = {}

    def fake_urlopen(req, timeout, context):
        capturado["priority"] = req.headers.get("Priority")
        capturado["actions"] = req.headers.get("Actions")
        return _FakeResp(200)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert notify.enviar_notificacion(
        "T", "m", prioridad="high", action_url="https://ntfy.sh/prueba-topic"
    ) is True
    assert capturado["priority"] == "high"
    import json

    assert json.loads(capturado["actions"])[0]["url"] == "https://ntfy.sh/prueba-topic"


def test_enviar_pendientes_incluye_prioridad(con_topic, monkeypatch):
    capturado = {}

    def fake_urlopen(req, timeout, context):
        capturado["priority"] = req.headers.get("Priority")
        capturado["actions"] = req.headers.get("Actions")
        return _FakeResp(200)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    tareas = [models.crear_tarea("urgente", prioridad="alta")]
    assert notify.enviar_pendientes(tareas) is True
    assert capturado["priority"] == "high"
    assert "Abrir" in capturado["actions"]


def test_hora_recordatorio_defecto(sin_topic):
    assert notify.hora_recordatorio() == "08:00"


def test_hora_recordatorio_desde_config(sin_topic, monkeypatch):
    monkeypatch.setattr(
        notify.storage,
        "cargar_config",
        lambda *a, **k: {"recordatorio_hora": "9:45", "ntfy_server": "https://ntfy.sh"},
    )
    assert notify.hora_recordatorio() == "09:45"


def test_hora_recordatorio_invalida_usa_defecto(sin_topic, monkeypatch):
    monkeypatch.setattr(
        notify.storage,
        "cargar_config",
        lambda *a, **k: {"recordatorio_hora": "25:99"},
    )
    assert notify.hora_recordatorio() == "08:00"


def test_enviar_notificacion_error_red(con_topic, monkeypatch, capsys):
    def fake_urlopen(req, timeout, context):
        raise OSError("sin red")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert notify.enviar_notificacion("T", "m") is False
    assert "No se pudo enviar" in capsys.readouterr().out


def test_construir_mensaje_con_pendientes():
    tareas = [
        models.crear_tarea("uno", tag="personal"),
        {"texto": "dos", "completada": True, "fecha": "2026-01-01T00:00:00", "tag": None, "prioridad": "media"},
    ]
    titulo, cuerpo, tags, prioridad = notify.construir_mensaje_pendientes(tareas)
    assert titulo == "Check List"
    assert tags == "memo"
    assert prioridad == "default"
    assert "Tienes 1 tarea pendiente" in cuerpo
    assert "• uno [personal]" in cuerpo


def test_construir_mensaje_sin_pendientes():
    titulo, cuerpo, tags, prioridad = notify.construir_mensaje_pendientes([])
    assert titulo == "Check List"
    assert cuerpo == "Todo al día 🎉"
    assert tags == "white_check_mark"
    assert prioridad == "default"


def test_construir_mensaje_prioridad_alta():
    tareas = [models.crear_tarea("urgente", prioridad="alta")]
    _, cuerpo, _, prioridad = notify.construir_mensaje_pendientes(tareas)
    assert prioridad == "high"
    assert "⚠" in cuerpo


def test_construir_mensaje_trunca(monkeypatch):
    monkeypatch.setattr(paths, "NTFY_LIMITE_BYTES", 50)
    tareas = [models.crear_tarea("x" * 100) for _ in range(5)]
    # ponerles fecha fija para ordenar igual
    for i, (real, t) in enumerate(models.obtener_pendientes_ordenados(tareas), 1):
        t["fecha"] = f"2026-01-0{i}T00:00:00"
    _, cuerpo, _, _ = notify.construir_mensaje_pendientes(tareas)
    assert "… y" in cuerpo


def test_header_seguro_dropping():
    assert notify._header_seguro("hola 😀") == "hola "