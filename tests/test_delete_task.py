import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from task_manager import create_task, delete_task, get_task, update_task, change_task_status, task_list

class TestDeleteTask:
    def setup_method(self):
        task_list.clear()
        task_list.extend([])
        create_task("A")

    def test_delete_existing_task(self):
        delete_task(1)
        assert len(task_list) == 0

    def test_deleted_task_cannot_be_found(self):
        delete_task(1)
        with pytest.raises(ValueError):
            get_task(1)
        with pytest.raises(ValueError):
            delete_task(1)
        with pytest.raises(ValueError):
            update_task(1, title="Z")
        with pytest.raises(ValueError):
            change_task_status(1, "DONE")
