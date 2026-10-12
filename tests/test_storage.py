import json

import pytest

from checklist import storage


@pytest.fixture
def tareas_path(tmp_path):
    return tmp_path / "tareas.json"


@pytest.fixture
def tags_path(tmp_path):
    return tmp_path / "tags.json"


@pytest.fixture
def config_path(tmp_path):
    return tmp_path / "config.json"


def test_guardar_y_cargar_tareas_roundtrip(tareas_path):
    tareas = [
        {"texto": "Comprar pan", "completada": False, "fecha": "2026-01-01T10:00:00", "tag": None, "prioridad": "media"},
        {"texto": "Estudiar", "completada": True, "fecha": "2026-01-02T10:00:00", "tag": "tareas", "prioridad": "alta"},
    ]
    storage.guardar_tareas(tareas, tareas_path)
    assert storage.cargar_tareas(tareas_path) == tareas


def test_cargar_tareas_sin_archivo(tareas_path):
    assert storage.cargar_tareas(tareas_path) == []


def test_cargar_tareas_normaliza_entradas_invalidas(tareas_path):
    data = [
        {"texto": "ok", "completada": False},
        "basura",
        42,
        {"texto": 123, "completada": "si", "fecha": 5, "tag": ["x"]},
    ]
    tareas_path.write_text(json.dumps(data), encoding="utf-8")
    result = storage.cargar_tareas(tareas_path)
    assert result == [
        {"texto": "ok", "completada": False, "fecha": None, "tag": None, "prioridad": "media"},
        {"texto": "123", "completada": True, "fecha": None, "tag": None, "prioridad": "media"},
    ]


def test_cargar_tareas_corrupto_hace_backup(tareas_path):
    tareas_path.write_text("{corrupto!!", encoding="utf-8")
    result = storage.cargar_tareas(tareas_path)
    assert result == []
    assert not tareas_path.exists()
    backups = list(tareas_path.parent.glob("tareas.json.corrupt-*"))
    assert len(backups) == 1


def test_cargar_tareas_correct_type_pero_no_lista(tareas_path):
    tareas_path.write_text('{"texto": "no soy una lista"}', encoding="utf-8")
    assert storage.cargar_tareas(tareas_path) == []
    assert not tareas_path.exists()


def test_cargar_tags_filtra_colores_invalidos(tags_path):
    tags_path.write_text(json.dumps({"ok": "rojo", "malo": "neon"}), encoding="utf-8")
    assert storage.cargar_tags(tags_path) == {"ok": "rojo"}


def test_cargar_tags_corrupto(tags_path):
    tags_path.write_text("##no json##", encoding="utf-8")
    assert storage.cargar_tags(tags_path) == {}
    assert not tags_path.exists()


def test_guardar_tags_roundtrip(tags_path):
    tags = {"proyectos": "rojo", "personal": "verde"}
    storage.guardar_tags(tags, tags_path)
    assert storage.cargar_tags(tags_path) == tags


def test_cargar_config_normaliza(config_path):
    config_path.write_text(
        json.dumps({"ntfy_topic": "abc", "ntfy_server": "https://x", "recordatorio_hora": "9:15", "extra": 1}),
        encoding="utf-8",
    )
    cfg = storage.cargar_config(config_path)
    assert cfg == {"ntfy_topic": "abc", "ntfy_server": "https://x", "recordatorio_hora": "09:15"}


def test_cargar_config_ignora_hora_invalida(config_path):
    config_path.write_text(
        json.dumps({"ntfy_topic": "abc", "recordatorio_hora": "25:99"}),
        encoding="utf-8",
    )
    cfg = storage.cargar_config(config_path)
    assert "recordatorio_hora" not in cfg


def test_cargar_config_sin_archivo(config_path):
    assert storage.cargar_config(config_path) == {}