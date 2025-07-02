import pytest
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import create_task, update_task, get_task, task_list

class TestUpdateTask:
    def setup_method(self):
        task_list.clear()
        create_task("Titre", "Desc")

    def test_update_title_only(self):
        update_task(1, title="Nouveau titre")
        t = get_task(1)
        assert t["title"] == "Nouveau titre"
        assert t["description"] == "Desc"

    def test_update_description_only(self):
        update_task(1, description="Nouvelle desc")
        t = get_task(1)
        assert t["title"] == "Titre"
        assert t["description"] == "Nouvelle desc"

    def test_update_both(self):
        update_task(1, title="X", description="Y")
        t = get_task(1)
        assert t["title"] == "X"
        assert t["description"] == "Y"

    def test_update_title_empty(self):
        with pytest.raises(ValueError) as exc:
            update_task(1, title="   ")
        assert str(exc.value) == "Title is required"

    def test_update_title_too_long(self):
        with pytest.raises(ValueError) as exc:
            update_task(1, title="x"*101)
        assert str(exc.value) == "Title cannot exceed 100 characters"

    def test_update_description_too_long(self):
        with pytest.raises(ValueError) as exc:
            update_task(1, description="x"*501)
        assert str(exc.value) == "Description cannot exceed 500 characters"

    def test_update_nonexistent_task(self):
        with pytest.raises(ValueError) as exc:
            update_task(999, title="A")
        assert str(exc.value) == "Task not found"

    def test_update_non_editable_fields_are_ignored(self):
        before = get_task(1).copy()
        update_task(1, title="Edited", description="Edited desc")
        after = get_task(1)
        assert after["id"] == before["id"]
        assert after["created_at"] == before["created_at"]
        assert after["status"] == before["status"]
