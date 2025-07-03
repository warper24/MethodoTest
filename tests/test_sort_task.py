import pytest
from src.task_manager import sort_tasks

@pytest.fixture
def sample_tasks():
    # Ordre aléatoire volontaire
    return [
        {"id": 1, "title": "Bravo", "status": "DONE",    "created_at": "2024-07-03T10:00:00", "priority": "LOW"},
        {"id": 2, "title": "Alpha", "status": "ONGOING", "created_at": "2024-07-02T08:00:00", "priority": "CRITICAL"},
        {"id": 3, "title": "Charlie", "status": "TODO",  "created_at": "2024-07-01T09:00:00", "priority": "NORMAL"},
        {"id": 4, "title": "Delta", "status": "ONGOING", "created_at": "2024-07-05T12:00:00", "priority": "HIGH"}
    ]

def test_sort_by_priority(sample_tasks):
    sorted_tasks = sort_tasks(sample_tasks, sort_by="priority", order="asc")
    prios = [t["priority"] for t in sorted_tasks]
    assert prios == ["CRITICAL", "HIGH", "NORMAL", "LOW"]

    sorted_tasks_desc = sort_tasks(sample_tasks, sort_by="priority", order="desc")
    prios_desc = [t["priority"] for t in sorted_tasks_desc]
    assert prios_desc == ["LOW", "NORMAL", "HIGH", "CRITICAL"]

def test_sort_by_status(sample_tasks):
    sorted_tasks = sort_tasks(sample_tasks, sort_by="status", order="asc")
    statuses = [t["status"] for t in sorted_tasks]
    # TODO < ONGOING < DONE
    assert statuses == ["TODO", "ONGOING", "ONGOING", "DONE"]

def test_sort_by_title(sample_tasks):
    sorted_tasks = sort_tasks(sample_tasks, sort_by="title", order="asc")
    titles = [t["title"] for t in sorted_tasks]
    assert titles == ["Alpha", "Bravo", "Charlie", "Delta"]

def test_sort_by_created_at(sample_tasks):
    sorted_tasks = sort_tasks(sample_tasks, sort_by="created_at", order="asc")
    created = [t["created_at"] for t in sorted_tasks]
    assert created == [
        "2024-07-01T09:00:00",
        "2024-07-02T08:00:00",
        "2024-07-03T10:00:00",
        "2024-07-05T12:00:00"
    ]

def test_invalid_sort_criteria(sample_tasks):
    with pytest.raises(ValueError, match="Invalid sort criteria"):
        sort_tasks(sample_tasks, sort_by="unknown")

def test_invalid_sort_order(sample_tasks):
    with pytest.raises(ValueError, match="Invalid sort order"):
        sort_tasks(sample_tasks, sort_by="title", order="up")
