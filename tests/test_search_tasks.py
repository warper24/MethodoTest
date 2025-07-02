import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import task_list, get_tasks, search_tasks

class TestSearchTasks:
    def setup_method(self):
        task_list.clear()
        # Ajout brut de tâches pour tester
        task_list.extend([
            {"id": 1, "title": "Rapport urgent", "description": "A rendre demain", "status": "TODO", "created_at": "2024-07-01T10:00:00"},
            {"id": 2, "title": "Faire les courses", "description": "Acheter du lait", "status": "DONE", "created_at": "2024-07-01T11:00:00"},
            {"id": 3, "title": "Rapport mensuel", "description": "Statistiques de ventes", "status": "ONGOING", "created_at": "2024-07-02T12:00:00"},
            {"id": 4, "title": "Lecture", "description": "Lire un roman", "status": "TODO", "created_at": "2024-07-03T09:00:00"},
        ])

    def test_search_in_title(self):
        results = search_tasks("Rapport")
        assert len(results) == 2
        assert all("Rapport" in t["title"] for t in results)

    def test_search_in_description(self):
        results = search_tasks("roman")
        assert len(results) == 1
        assert results[0]["title"] == "Lecture"

    def test_search_in_title_and_description(self):
        results = search_tasks("du")
        assert len(results) == 1
        assert results[0]["title"] == "Faire les courses"

    def test_search_empty_returns_all(self):
        results = search_tasks("")
        assert len(results) == 4

    def test_search_case_insensitive(self):
        results = search_tasks("rApPoRt")
        assert len(results) == 2

    def test_search_no_result(self):
        results = search_tasks("pizza")
        assert results == []

    def test_search_paginated(self):
        # Ajoute 20 tâches brutes supplémentaires
        task_list.extend([
            {"id": i+5, "title": f"Tâche {i}", "description": "description", "status": "TODO", "created_at": f"2024-07-04T10:{i:02d}:00"}
            for i in range(20)
        ])
        results = search_tasks("", page=2, page_size=10)
        assert len(results) == 10

    def test_search_tasks_via_get_tasks(self):
        results = get_tasks(keyword="rapport", page=1, page_size=10)
        assert len(results) == 2
