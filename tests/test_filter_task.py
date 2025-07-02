import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import task_list, filter_tasks_by_status, get_tasks

class TestFilterTasksByStatus:
    def setup_method(self):
        task_list.clear()
        task_list.extend([
            {"id": 1, "title": "Tâche TODO", "description": "Desc", "status": "TODO", "created_at": "2024-07-01T10:00:00"},
            {"id": 2, "title": "Tâche ONGOING", "description": "Desc", "status": "ONGOING", "created_at": "2024-07-01T11:00:00"},
            {"id": 3, "title": "Tâche DONE", "description": "Desc", "status": "DONE", "created_at": "2024-07-01T12:00:00"},
        ])

    def test_filter_todo(self):
        results = filter_tasks_by_status("TODO")
        assert len(results) == 1
        assert results[0]["status"] == "TODO"

    def test_filter_ongoing(self):
        results = filter_tasks_by_status("ONGOING")
        assert len(results) == 1
        assert results[0]["status"] == "ONGOING"

    def test_filter_done(self):
        results = filter_tasks_by_status("DONE")
        assert len(results) == 1
        assert results[0]["status"] == "DONE"

    def test_filter_none_found(self):
        # On retire la seule TODO
        task_list[0]["status"] = "DONE"
        results = filter_tasks_by_status("TODO")
        assert results == []

    def test_filter_invalid_status(self):
        with pytest.raises(ValueError) as exc:
            filter_tasks_by_status("INVALID")
        assert str(exc.value) == "Invalid filter status"

    def test_filter_paginated(self):
        # Ajoute 15 tâches supplémentaires avec le même statut
        task_list.extend([
            {"id": i+4, "title": f"Task {i}", "description": "", "status": "DONE", "created_at": f"2024-07-02T10:{i:02d}:00"}
            for i in range(15)
        ])
        results = filter_tasks_by_status("DONE", page=2, page_size=5)
        assert len(results) == 5

    def test_filter_status_via_get_tasks(self):
        results = get_tasks(status="TODO", page=1, page_size=10)
        assert all(r["status"] == "TODO" for r in results)
