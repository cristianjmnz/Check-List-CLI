import json
import re

import pytest

from checklist import cli, paths, storage, ui


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
    monkeypatch.setattr(paths, "DB", tmp_path / "tareas.db")
    return tmp_path


def test_add_crea_tarea(data_dir, capsys):
    data_dir.joinpath("tags.json").write_text(
        json.dumps({"personal": "verde"}), encoding="utf-8"
    )
    assert cli.main(["add", "Comprar pan", "-t", "personal"]) == 0
    tareas = storage.cargar_tareas()
    assert len(tareas) == 1
    assert tareas[0]["texto"] == "Comprar pan"
    assert tareas[0]["tag"] == "personal"
    assert "Tarea añadida" in capsys.readouterr().out


def test_add_con_tag_invalido(data_dir):
    cli.main(["add", "Sin tag"])
    cli.main(["add", "Con tag", "-t", "inexistente"])
    tareas = storage.cargar_tareas()
    assert tareas[0]["tag"] is None
    assert tareas[1]["tag"] is None


def test_add_con_prioridad(data_dir):
    cli.main(["add", "tarea urgente", "-p", "alta"])
    cli.main(["add", "tarea normal"])
    tareas = storage.cargar_tareas()
    assert tareas[0]["prioridad"] == "alta"
    assert tareas[1]["prioridad"] == "media"


def test_reminder_muestra_hora_defecto(data_dir, capsys):
    assert cli.main(["reminder"]) == 0
    assert "08:00" in capsys.readouterr().out


def test_reminder_fija_hora(data_dir, capsys):
    assert cli.main(["reminder", "9:30"]) == 0
    assert storage.cargar_config()["recordatorio_hora"] == "09:30"
    cli.main(["reminder"])
    assert "09:30" in capsys.readouterr().out


def test_reminder_hora_invalida(data_dir, capsys):
    assert cli.main(["reminder", "25:99"]) == 1
    assert "Hora no válida" in capsys.readouterr().out


def test_done_por_numero_de_pendiente(data_dir):
    cli.main(["add", "a"])
    cli.main(["add", "b"])
    cli.main(["add", "c"])
    assert cli.main(["done", "1"]) == 0
    tareas = storage.cargar_tareas()
    assert sum(1 for t in tareas if t["completada"]) == 1
    assert cli.main(["done", "0"]) == 1
    assert cli.main(["done", "99"]) == 1


def test_rm_por_numero_de_pendiente(data_dir):
    cli.main(["add", "a"])
    cli.main(["add", "b"])
    cli.main(["rm", "1"])
    tareas = storage.cargar_tareas()
    assert [t["texto"] for t in tareas] == ["a"]


def test_list_muestra_pendientes(data_dir, capsys):
    cli.main(["add", "primera"])
    cli.main(["add", "segunda"])
    cli.main(["list"])
    out = capsys.readouterr().out
    assert "primera" in out
    assert "segunda" in out


def test_topic_set(data_dir, capsys):
    assert cli.main(["topic", "--set", "mi-topic"]) == 0
    assert storage.cargar_config()["ntfy_topic"] == "mi-topic"
    cli.main(["topic"])
    assert "mi-topic" in capsys.readouterr().out


def test_legacy_set_topic(data_dir):
    assert cli.main(["--set-topic", "legacy"]) == 0
    assert storage.cargar_config()["ntfy_topic"] == "legacy"


def test_menu_por_defecto_sin_comandos_termina_con_eof(data_dir, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a: (_ for _ in ()).throw(EOFError()))
    assert cli.main([]) == 0


def test_topic_set_vacio_rechazado(data_dir, capsys):
    assert cli.main(["topic", "--set", "   "]) == 1
    assert "vac" in capsys.readouterr().out.lower()
    assert "ntfy_topic" not in storage.cargar_config()


def test_buscar_tarea_usa_numeracion_de_pendientes(data_dir, monkeypatch, capsys):
    cli.main(["add", "primera tarea"])
    cli.main(["add", "segunda tarea"])
    tareas = storage.cargar_tareas()

    monkeypatch.setattr("builtins.input", lambda *a: "tarea")
    ui.buscar_tarea(tareas)

    limpio = re.sub(r"\x1b\[[0-9;]*m", "", capsys.readouterr().out)
    assert "1 [○] segunda tarea" in limpio
    assert "2 [○] primera tarea" in limpio


def test_error_bd_muestra_mensaje_amable(data_dir, monkeypatch, capsys):
    import sqlite3

    def boom():
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(storage, "cargar_tareas", boom)
    assert cli.main(["list"]) == 1
    assert "Error al acceder a la base de datos" in capsys.readouterr().out


def test_imprimir_tarea_usa_tag(data_dir, capsys):
    data_dir.joinpath("tags.json").write_text(
        json.dumps({"personal": "verde"}), encoding="utf-8"
    )
    cli.main(["add", "tarea con tag", "-t", "personal"])
    cli.main(["list"])
    out = capsys.readouterr().out
    assert "[personal]" in out


def test_sync_llama_a_procesar(data_dir, monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        cli.sync,
        "procesar_comandos",
        lambda silencioso=False: llamadas.append(silencioso) or 0,
    )
    assert cli.main(["sync"]) == 0
    assert llamadas == [False]


def test_list_sincroniza_en_silencio(data_dir, monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        cli.sync,
        "procesar_comandos",
        lambda silencioso=False: llamadas.append(silencioso) or 0,
    )
    cli.main(["list"])
    assert llamadas == [True]


def test_notify_sincroniza_antes_de_enviar(data_dir, monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        cli.sync,
        "procesar_comandos",
        lambda silencioso=False: llamadas.append(silencioso) or 0,
    )
    monkeypatch.setattr(cli.notify, "enviar_pendientes", lambda tareas: True)
    assert cli.main(["notify"]) == 0
    assert llamadas == [True]
