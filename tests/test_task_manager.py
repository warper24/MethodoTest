import pytest
from datetime import datetime
import sys
import os

# Pour pouvoir importer src/task_manager.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from task_manager import create_task, task_list

class TestCreateTask:
    def setup_method(self):
        """Réinitialise la liste avant chaque test."""
        task_list.clear()

    def test_create_with_valid_title_only(self):
        task = create_task("Nouvelle tâche")
        assert task["id"] == 1
        assert task["title"] == "Nouvelle tâche"
        assert task["description"] == ""
        assert task["status"] == "TODO"
        # Vérifie le champ created_at au format ISO
        assert "created_at" in task
        dt = datetime.fromisoformat(task["created_at"])
        assert isinstance(dt, datetime)

    def test_create_with_title_and_description(self):
        desc = "Une description valide"
        task = create_task("Tâche", desc)
        assert task["description"] == desc

    def test_empty_title_raises(self):
        with pytest.raises(ValueError) as exc:
            create_task("   ")
        assert str(exc.value) == "Title is required"

    def test_title_too_long_raises(self):
        long_title = "x" * 101
        with pytest.raises(ValueError) as exc:
            create_task(long_title)
        assert str(exc.value) == "Title cannot exceed 100 characters"

    def test_description_too_long_raises(self):
        long_desc = "x" * 501
        with pytest.raises(ValueError) as exc:
            create_task("Tâche valide", long_desc)
        assert str(exc.value) == "Description cannot exceed 500 characters"

    def test_title_trimming(self):
        task = create_task("  Trim  ")
        assert task["title"] == "Trim"
