import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import change_task_status, get_task, task_list

class TestChangeTaskStatus:
    def setup_method(self):
        task_list.clear()
        task_list.append({
            "id": 1,
            "title": "Titre",
            "description": "Desc",
            "status": "TODO",
            "created_at": "2024-07-01T10:00:00"
        })

    def test_status_valid(self):
        for s in ("TODO", "ONGOING", "DONE"):
            change_task_status(1, s)
            t = get_task(1)
            assert t["status"] == s

    def test_status_invalid(self):
        with pytest.raises(ValueError) as exc:
            change_task_status(1, "NOTASTATUS")
        assert "Invalid status" in str(exc.value)

    def test_status_nonexistent_task(self):
        with pytest.raises(ValueError) as exc:
            change_task_status(999, "DONE")
        assert str(exc.value) == "Task not found"
