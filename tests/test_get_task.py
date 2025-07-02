import pytest
from datetime import datetime
import sys
import os

# Permet l'import depuis src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from task_manager import get_task, task_list

class TestGetTask:
    def setup_method(self):
        """Réinitialise la liste avant chaque test et ajoute une tâche d'exemple."""
        task_list.clear()
        task_list.append({
            "id": 1,
            "title": "Tâche A",
            "description": "Desc A",
            "status": "TODO",
            "created_at": datetime.now().isoformat(timespec="seconds")
        })

    def test_get_existing_task(self):
        task = get_task(1)
        assert isinstance(task, dict)
        assert task["id"] == 1
        assert "title" in task
        assert "description" in task
        assert "status" in task
        assert "created_at" in task
        # Vérifie le format ISO de created_at
        dt = datetime.fromisoformat(task["created_at"])
        assert isinstance(dt, datetime)

    def test_get_nonexistent_task_raises(self):
        with pytest.raises(ValueError) as exc:
            get_task(999)
        assert str(exc.value) == "Task not found"

    def test_get_invalid_id_format_raises(self):
        with pytest.raises(ValueError) as exc:
            get_task("abc")
        assert str(exc.value) == "Invalid ID format"
