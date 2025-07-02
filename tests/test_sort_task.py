import pytest
import sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import create_task, sort_tasks, task_list, change_task_status

class TestSortTasks:
    def setup_method(self):
        task_list.clear()
        # Crée 3 tâches à des dates et titres différents
        now = datetime.now()
        t1 = create_task("b-titre", "desc")
        t1["created_at"] = (now - timedelta(days=2)).isoformat(timespec="seconds")
        t2 = create_task("c-titre", "desc")
        t2["created_at"] = (now - timedelta(days=1)).isoformat(timespec="seconds")
        t3 = create_task("a-titre", "desc")
        t3["created_at"] = now.isoformat(timespec="seconds")
        change_task_status(t2["id"], "ONGOING")
        change_task_status(t3["id"], "DONE")

    def test_sort_by_date_asc(self):
        sorted_ = sort_tasks(task_list, sort_by="created_at", order="asc")
        assert [t["title"] for t in sorted_] == ["b-titre", "c-titre", "a-titre"]

    def test_sort_by_date_desc(self):
        sorted_ = sort_tasks(task_list, sort_by="created_at", order="desc")
        assert [t["title"] for t in sorted_] == ["a-titre", "c-titre", "b-titre"]

    def test_sort_by_title_asc(self):
        sorted_ = sort_tasks(task_list, sort_by="title", order="asc")
        assert [t["title"] for t in sorted_] == ["a-titre", "b-titre", "c-titre"]

    def test_sort_by_title_desc(self):
        sorted_ = sort_tasks(task_list, sort_by="title", order="desc")
        assert [t["title"] for t in sorted_] == ["c-titre", "b-titre", "a-titre"]

    def test_sort_by_status(self):
        sorted_ = sort_tasks(task_list, sort_by="status", order="asc")
        # Ordre: TODO, ONGOING, DONE
        assert [t["status"] for t in sorted_] == ["TODO", "ONGOING", "DONE"]

    def test_default_sort(self):
        sorted_ = sort_tasks(task_list)  # created_at, desc
        assert [t["title"] for t in sorted_] == ["a-titre", "c-titre", "b-titre"]

    def test_invalid_sort_criteria(self):
        with pytest.raises(ValueError):
            sort_tasks(task_list, sort_by="invalid")
        with pytest.raises(ValueError):
            sort_tasks(task_list, order="wrong")
