import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import create_task, change_task_status, filter_tasks_by_status, task_list

class TestFilterTasksByStatus:
    def setup_method(self):
        task_list.clear()
        create_task("Tâche TODO")
        create_task("Tâche ONGOING")
        create_task("Tâche DONE")
        change_task_status(2, "ONGOING")
        change_task_status(3, "DONE")

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
        # Change all tasks to DONE
        change_task_status(1, "DONE")
        change_task_status(2, "DONE")
        results = filter_tasks_by_status("TODO")
        assert results == []

    def test_filter_invalid_status(self):
        with pytest.raises(ValueError) as exc:
            filter_tasks_by_status("INVALID")
        assert str(exc.value) == "Invalid filter status"

    def test_filter_paginated(self):
        # Add many DONE tasks
        for i in range(15):
            t = create_task(f"Task {i}")
            change_task_status(t["id"], "DONE")
        results = filter_tasks_by_status("DONE", page=2, page_size=5)
        assert len(results) == 5  # Page 2, taille 5
