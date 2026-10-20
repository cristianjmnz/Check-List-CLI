import io
import json
import urllib.error
import urllib.request

import pytest

from checklist import models, paths, storage, sync


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    monkeypatch.delenv("NTFY_SERVER", raising=False)
    monkeypatch.setattr(paths, "DB", tmp_path / "tareas.db")
    return tmp_path


def _config(token="tok123", last_id=None):
    cfg = {
        "ntfy_topic": "principal",
        "ntfy_server": "https://ntfy.sh",
        "ntfy_cmd_topic": "cmd-test",
        "ntfy_cmd_token": token,
    }
    if last_id is not None:
        cfg["ntfy_last_id"] = last_id
    storage.guardar_config(cfg)


def _respuesta(mensajes):
    lineas = [json.dumps(m).encode("utf-8") + b"\n" for m in mensajes]
    return io.BytesIO(b"".join(lineas))


def _mensaje(texto, msg_id="m1", event="message"):
    return {"id": msg_id, "event": event, "message": texto}


def _tarea_id():
    storage.guardar_tareas([models.crear_tarea("comprar pan")])
    return storage.cargar_tareas()[0]["id"]


def test_parse_comando():
    assert sync._parse_comando("done:3:tok") == (3, "tok")
    assert sync._parse_comando("  done:12:abc_DEF-1  ") == (12, "abc_DEF-1")
    assert sync._parse_comando("done:x:tok") is None
    assert sync._parse_comando("nada") is None
    assert sync._parse_comando(None) is None


def test_sin_config_no_hace_nada(db):
    assert sync.procesar_comandos() == 0


def test_marca_tarea_completada_y_guarda_last_id(db, monkeypatch):
    _config()
    tarea_id = _tarea_id()
    capturado = {}

    def fake_urlopen(url, timeout=None, context=None):
        capturado["url"] = url
        return _respuesta([_mensaje(f"done:{tarea_id}:tok123")])

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert sync.procesar_comandos() == 1
    assert storage.cargar_tareas()[0]["completada"] is True
    assert storage.cargar_config()["ntfy_last_id"] == "m1"
    assert "since=all" in capturado["url"]
    assert "poll=1" in capturado["url"]


def test_token_invalido_no_completa_pero_avanza(db, monkeypatch):
    _config()
    tarea_id = _tarea_id()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta(
            [_mensaje(f"done:{tarea_id}:malo")]
        ),
    )

    assert sync.procesar_comandos() == 0
    assert storage.cargar_tareas()[0]["completada"] is False
    assert storage.cargar_config()["ntfy_last_id"] == "m1"


def test_id_inexistente_no_falla(db, monkeypatch):
    _config()
    _tarea_id()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta(
            [_mensaje("done:9999:tok123")]
        ),
    )

    assert sync.procesar_comandos() == 0


def test_es_idempotente(db, monkeypatch):
    _config()
    tarea_id = _tarea_id()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta(
            [_mensaje(f"done:{tarea_id}:tok123")]
        ),
    )

    assert sync.procesar_comandos() == 1
    assert sync.procesar_comandos() == 0
    assert storage.cargar_tareas()[0]["completada"] is True


def test_ignora_eventos_que_no_son_mensajes(db, monkeypatch):
    _config(last_id="previo")

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta(
            [
                _mensaje("", msg_id="open1", event="open"),
                _mensaje("", msg_id="keep1", event="keepalive"),
            ]
        ),
    )

    assert sync.procesar_comandos() == 0
    assert storage.cargar_config()["ntfy_last_id"] == "previo"


def test_usa_ultimo_id_como_since(db, monkeypatch):
    _config(last_id="abc")
    capturado = {}

    def fake_urlopen(url, timeout=None, context=None):
        capturado["url"] = url
        return _respuesta([])

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    sync.procesar_comandos()
    assert "since=abc" in capturado["url"]


def test_silencioso_reporta_completadas(db, monkeypatch, capsys):
    _config()
    tarea_id = _tarea_id()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta(
            [_mensaje(f"done:{tarea_id}:tok123")]
        ),
    )

    assert sync.procesar_comandos(silencioso=True) == 1
    assert "completada" in capsys.readouterr().out


def test_silencioso_calla_si_no_hay_comandos(db, monkeypatch, capsys):
    _config()
    _tarea_id()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda url, timeout=None, context=None: _respuesta([]),
    )

    assert sync.procesar_comandos(silencioso=True) == 0
    assert capsys.readouterr().out == ""


def test_error_de_red_no_revienta(db, monkeypatch, capsys):
    _config()

    def fake_urlopen(url, timeout=None, context=None):
        raise urllib.error.URLError("sin red")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert sync.procesar_comandos(silencioso=True) == 0
    assert capsys.readouterr().out == ""

    assert sync.procesar_comandos() == 0
    assert "No se pudo sincronizar" in capsys.readouterr().out
