import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import (
    create_task, get_task, update_task, change_task_status, delete_task,
    get_tasks, search_tasks, task_list
)

# ------------------ US004 - Changer le statut d'une tâche ------------------

class TestTaskStatus:
    def setup_method(self):
        task_list.clear()
        create_task("Tâche à faire")

    def test_change_status_valid(self):
        for status in ["TODO", "ONGOING", "DONE"]:
            change_task_status(1, status)
            t = get_task(1)
            assert t["status"] == status

    def test_change_status_invalid_value(self):
        with pytest.raises(ValueError) as exc:
            change_task_status(1, "INVALID")
        assert "Invalid status" in str(exc.value)

    def test_change_status_nonexistent_task(self):
        with pytest.raises(ValueError) as exc:
            change_task_status(999, "DONE")
        assert str(exc.value) == "Task not found"

# ------------------ US005 - Supprimer une tâche ------------------

class TestTaskDelete:
    def setup_method(self):
        task_list.clear()
        create_task("A supprimer")

    def test_delete_existing_task(self):
        delete_task(1)
        assert get_tasks() == []

    def test_delete_then_access(self):
        delete_task(1)
        # Consulter, supprimer, modifier, changer status => Task not found
        with pytest.raises(ValueError):
            get_task(1)
        with pytest.raises(ValueError):
            delete_task(1)
        with pytest.raises(ValueError):
            update_task(1, title="X")
        with pytest.raises(ValueError):
            change_task_status(1, "DONE")

# ------------------ US006 - Pagination des tâches ------------------

class TestTaskPagination:
    def setup_method(self):
        task_list.clear()
        for i in range(25):
            create_task(f"Tâche {i+1}")

    def test_first_page_size_10(self):
        page = 1
        page_size = 10
        tasks, pagination = get_tasks(page=page, page_size=page_size, return_pagination=True)
        assert len(tasks) == 10
        assert pagination["current_page"] == 1
        assert pagination["total_pages"] == 3
        assert pagination["total_items"] == 25

    def test_second_page_size_10(self):
        tasks, pagination = get_tasks(page=2, page_size=10, return_pagination=True)
        assert len(tasks) == 10
        assert pagination["current_page"] == 2

    def test_beyond_last_page(self):
        tasks, pagination = get_tasks(page=4, page_size=10, return_pagination=True)
        assert tasks == []
        assert pagination["current_page"] == 4
        assert pagination["total_pages"] == 3

    def test_default_page_and_size(self):
        tasks, pagination = get_tasks(return_pagination=True)
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 20
        assert len(tasks) == 20

    def test_invalid_page_size(self):
        with pytest.raises(ValueError) as exc:
            get_tasks(page=1, page_size=0)
        assert str(exc.value) == "Invalid page size"
        with pytest.raises(ValueError) as exc2:
            get_tasks(page=1, page_size=-3)
        assert str(exc2.value) == "Invalid page size"

    def test_no_tasks(self):
        task_list.clear()
        tasks, pagination = get_tasks(return_pagination=True)
        assert tasks == []
        assert pagination["total_items"] == 0
        assert pagination["total_pages"] == 0