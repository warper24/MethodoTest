from src.task_manager import create_task, set_due_date, change_task_status, is_overdue, get_overdue_tasks, task_list
from datetime import datetime, timedelta

def setup_function(function):
    task_list.clear()

def test_todo_overdue():
    # Tâche TODO, échéance passée
    past_date = (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds")
    t = create_task("Retard", due_date=past_date)
    assert is_overdue(t)
    assert t in get_overdue_tasks()

def test_ongoing_overdue():
    past_date = (datetime.now() - timedelta(days=2)).isoformat(timespec="seconds")
    t = create_task("Ongoing", due_date=past_date)
    change_task_status(t["id"], "ONGOING")
    assert is_overdue(t)
    assert t in get_overdue_tasks()

def test_done_not_overdue():
    past_date = (datetime.now() - timedelta(days=3)).isoformat(timespec="seconds")
    t = create_task("Finie", due_date=past_date)
    change_task_status(t["id"], "DONE")
    assert not is_overdue(t)
    assert t not in get_overdue_tasks()

def test_future_due_date():
    future_date = (datetime.now() + timedelta(days=2)).isoformat(timespec="seconds")
    t = create_task("Future", due_date=future_date)
    assert not is_overdue(t)
    assert t not in get_overdue_tasks()

def test_no_due_date():
    t = create_task("Sans échéance")
    assert not is_overdue(t)
    assert t not in get_overdue_tasks()

def test_today_due_date_not_overdue():
    today = datetime.now().date().isoformat()
    t = create_task("Aujourd'hui", due_date=today)
    assert not is_overdue(t)
