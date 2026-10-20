import json
import sqlite3

import pytest

from checklist import storage


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "tareas.db"


def _sin_id(t):
    return {k: v for k, v in t.items() if k != "id"}


def test_guardar_y_cargar_tareas_roundtrip(db_path):
    tareas = [
        {"texto": "Comprar pan", "completada": False, "fecha": "2026-01-01T10:00:00", "tag": None, "prioridad": "media"},
        {"texto": "Estudiar", "completada": True, "fecha": "2026-01-02T10:00:00", "tag": "tareas", "prioridad": "alta"},
    ]
    storage.guardar_tareas(tareas, db_path)
    result = storage.cargar_tareas(db_path)
    assert [_sin_id(t) for t in result] == [_sin_id(t) for t in tareas]
    assert all(t["id"] >= 1 for t in result)


def test_ids_estables_al_releer(db_path):
    storage.guardar_tareas([{"texto": "a", "completada": False, "fecha": None, "tag": None, "prioridad": "media"}], db_path)
    r1 = storage.cargar_tareas(db_path)
    r1[0]["completada"] = True
    storage.guardar_tareas(r1, db_path)
    r2 = storage.cargar_tareas(db_path)
    assert r2 == r1
    assert r2[0]["completada"] is True


def test_guardar_tareas_borra_filas_ausentes(db_path):
    storage.guardar_tareas(
        [
            {"texto": "a", "completada": False, "fecha": None, "tag": None, "prioridad": "media"},
            {"texto": "b", "completada": False, "fecha": None, "tag": None, "prioridad": "media"},
        ],
        db_path,
    )
    cargadas = storage.cargar_tareas(db_path)
    cargadas.pop(1)
    storage.guardar_tareas(cargadas, db_path)
    assert [t["texto"] for t in storage.cargar_tareas(db_path)] == ["a"]


def test_cargar_tareas_sin_archivo(db_path):
    assert storage.cargar_tareas(db_path) == []


def test_migracion_desde_json(db_path):
    db_path.parent.joinpath("tareas.json").write_text(
        json.dumps(
            [
                {"texto": "ok", "completada": False},
                "basura",
                42,
                {"texto": 123, "completada": "si", "fecha": 5, "tag": ["x"]},
            ]
        ),
        encoding="utf-8",
    )
    tareas = storage.cargar_tareas(db_path)
    assert [_sin_id(t) for t in tareas] == [
        {"texto": "ok", "completada": False, "fecha": None, "tag": None, "prioridad": "media"},
        {"texto": "123", "completada": True, "fecha": None, "tag": None, "prioridad": "media"},
    ]
    assert db_path.exists()


def test_migracion_copia_tags_y_config(db_path):
    json_dir = db_path.parent
    json_dir.joinpath("tareas.json").write_text(json.dumps([{"texto": "a"}]), encoding="utf-8")
    json_dir.joinpath("tags.json").write_text(json.dumps({"ok": "rojo", "malo": "neon"}), encoding="utf-8")
    json_dir.joinpath("config.json").write_text(
        json.dumps({"ntfy_topic": "abc", "recordatorio_hora": "9:15", "extra": 1}),
        encoding="utf-8",
    )
    storage.cargar_tareas(db_path)
    assert storage.cargar_tags(db_path) == {"ok": "rojo"}
    assert storage.cargar_config(db_path) == {
        "ntfy_topic": "abc",
        "recordatorio_hora": "09:15",
    }
    assert json_dir.joinpath("tareas.json").exists()
    assert json_dir.joinpath("config.json").exists()


def test_cargar_tareas_corrupto_hace_backup(db_path):
    db_path.write_bytes(b"no es una base sqlite")
    assert storage.cargar_tareas(db_path) == []
    backups = list(db_path.parent.glob("tareas.db.corrupt-*"))
    assert len(backups) == 1


def test_es_corrupcion_distingue_bloqueo():
    corrupto = sqlite3.DatabaseError("file is not a database")
    bloqueo = sqlite3.OperationalError("database is locked")
    assert storage._es_corrupcion(corrupto) is True
    assert storage._es_corrupcion(bloqueo) is False


def test_bloqueo_no_se_confunde_con_corrupcion(db_path, monkeypatch):
    db_path.write_bytes(b"contenido previo")

    def bloqueado(_path):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(storage, "_abrir_db", bloqueado)
    with pytest.raises(sqlite3.OperationalError):
        storage.cargar_tareas(db_path)
    assert db_path.exists()
    assert list(db_path.parent.glob("tareas.db.corrupt-*")) == []


def test_guardar_tareas_recupera_db_corrupta(db_path):
    db_path.write_bytes(b"no es una base sqlite")
    storage.guardar_tareas(
        [{"texto": "nueva", "completada": False, "fecha": None, "tag": None, "prioridad": "media"}],
        db_path,
    )
    assert [t["texto"] for t in storage.cargar_tareas(db_path)] == ["nueva"]
    assert len(list(db_path.parent.glob("tareas.db.corrupt-*"))) == 1


def test_cargar_tags_corrupto_recupera(db_path):
    db_path.write_bytes(b"no es una base sqlite")
    assert storage.cargar_tags(db_path) == {}
    assert len(list(db_path.parent.glob("tareas.db.corrupt-*"))) == 1
    storage.guardar_tags({"ok": "rojo"}, db_path)
    assert storage.cargar_tags(db_path) == {"ok": "rojo"}


def test_tags_roundtrip(db_path):
    tags = {"proyectos": "rojo", "personal": "verde"}
    storage.guardar_tags(tags, db_path)
    assert storage.cargar_tags(db_path) == tags


def test_cargar_tags_filtra_colores_invalidos(db_path):
    storage.guardar_tags({"ok": "rojo", "malo": "neon"}, db_path)
    assert storage.cargar_tags(db_path) == {"ok": "rojo"}


def test_config_roundtrip_y_normalizacion(db_path):
    storage.guardar_config(
        {"ntfy_topic": "abc", "ntfy_server": "https://x", "recordatorio_hora": "9:15", "extra": 1},
        db_path,
    )
    assert storage.cargar_config(db_path) == {
        "ntfy_topic": "abc",
        "ntfy_server": "https://x",
        "recordatorio_hora": "09:15",
    }


def test_cargar_config_ignora_hora_invalida(db_path):
    storage.guardar_config({"ntfy_topic": "abc", "recordatorio_hora": "25:99"}, db_path)
    cfg = storage.cargar_config(db_path)
    assert "recordatorio_hora" not in cfg


def test_cargar_config_sin_archivo(db_path):
    assert storage.cargar_config(db_path) == {}


def test_actualizar_config_conserva_otras_claves(db_path):
    storage.guardar_config(
        {"ntfy_topic": "abc", "recordatorio_hora": "09:00"}, db_path
    )
    storage.actualizar_config({"ntfy_last_id": "xyz"}, db_path)
    assert storage.cargar_config(db_path) == {
        "ntfy_topic": "abc",
        "recordatorio_hora": "09:00",
        "ntfy_last_id": "xyz",
    }

