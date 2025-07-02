import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import create_task, search_tasks, task_list

class TestSearchTasks:
    def setup_method(self):
        task_list.clear()
        create_task("Rapport urgent", "A rendre demain")
        create_task("Faire les courses", "Acheter du lait")
        create_task("Rapport mensuel", "Statistiques de ventes")
        create_task("Lecture", "Lire un roman")

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
        # Ajoute des tâches pour avoir plus de résultats
        for i in range(20):
            create_task(f"Tâche {i}", "description")
        results = search_tasks("", page=2, page_size=10)
        assert len(results) == 10
