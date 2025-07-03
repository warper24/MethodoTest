import pytest
from src import task_manager

def test_create_calls_save(tmp_path, monkeypatch):
    calls = []
    def fake_save(tasks):
        calls.append(tasks)
    monkeypatch.setattr(task_manager, "_save_tasks", fake_save)

    t = task_manager.create_task("Nouvelle")
    assert calls, "On attend au moins un appel à _save_tasks"
    assert t in calls[-1]
