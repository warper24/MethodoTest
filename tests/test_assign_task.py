from src.task_manager import create_task, assign_task, task_list
import pytest

class TestAssignTask:

    def setup_method(self):
        # Reset tâches
        task_list.clear()
        task_list.append({
            "id": 1,
            "title": "Tâche A",
            "description": "",
            "status": "TODO",
            "created_at": "2025-07-01T12:00:00"
        })

        # Mock users.json
        with open("users.json", "w", encoding="utf-8") as f:
            import json
            json.dump([
                {"id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2025-07-01T12:00:00"},
                {"id": 2, "name": "Bob", "email": "bob@example.com", "created_at": "2025-07-01T12:01:00"}
            ], f, ensure_ascii=False, indent=2)

    def test_assign_existing_task_to_existing_user(self):
        task = assign_task(1, 2)
        assert task["assignee_id"] == 2

    def test_reassign_task_to_another_user(self):
        assign_task(1, 1)
        task = assign_task(1, 2)
        assert task["assignee_id"] == 2

    def test_unassign_task(self):
        assign_task(1, 1)
        task = assign_task(1, None)
        assert task.get("assignee_id") is None

    def test_assign_task_to_nonexistent_user(self):
        with pytest.raises(ValueError, match="User not found"):
            assign_task(1, 999)

    def test_assign_nonexistent_task(self):
        with pytest.raises(ValueError, match="Task not found"):
            assign_task(999, 1)
