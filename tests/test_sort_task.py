import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import task_list, get_tasks, sort_tasks

class TestSortTasks:
    def setup_method(self):
        task_list.clear()
        task_list.extend([
            {"id": 1, "title": "b-titre", "description": "", "status": "TODO", "created_at": "2024-07-01T08:00:00"},
            {"id": 2, "title": "c-titre", "description": "", "status": "ONGOING", "created_at": "2024-07-02T09:00:00"},
            {"id": 3, "title": "a-titre", "description": "", "status": "DONE", "created_at": "2024-07-03T10:00:00"},
        ])

    def test_sort_by_date_asc(self):
        sorted_ = get_tasks(sort_by="created_at", order="asc", page_size=10)
        assert [t["title"] for t in sorted_] == ["b-titre", "c-titre", "a-titre"]

    def test_sort_by_date_desc(self):
        sorted_ = get_tasks(sort_by="created_at", order="desc", page_size=10)
        assert [t["title"] for t in sorted_] == ["a-titre", "c-titre", "b-titre"]

    def test_sort_by_title_asc(self):
        sorted_ = get_tasks(sort_by="title", order="asc", page_size=10)
        assert [t["title"] for t in sorted_] == ["a-titre", "b-titre", "c-titre"]

    def test_sort_by_title_desc(self):
        sorted_ = get_tasks(sort_by="title", order="desc", page_size=10)
        assert [t["title"] for t in sorted_] == ["c-titre", "b-titre", "a-titre"]

    def test_sort_by_status(self):
        sorted_ = get_tasks(sort_by="status", order="asc", page_size=10)
        assert [t["status"] for t in sorted_] == ["TODO", "ONGOING", "DONE"]

    def test_default_sort(self):
        sorted_ = get_tasks(page_size=10)  # created_at, desc
        assert [t["title"] for t in sorted_] == ["a-titre", "c-titre", "b-titre"]

    def test_invalid_sort_criteria(self):
        with pytest.raises(ValueError):
            get_tasks(sort_by="invalid", page_size=10)
        with pytest.raises(ValueError):
            get_tasks(order="wrong", page_size=10)
