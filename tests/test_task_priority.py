import pytest
from src.task_manager import create_task, set_task_priority, get_tasks, task_list

def setup_function(function):
    task_list.clear()

def test_priority_set_and_default():
    t1 = create_task("Tâche normale")
    assert t1["priority"] == "NORMAL"
    t2 = create_task("Tâche haute", priority="HIGH")
    assert t2["priority"] == "HIGH"
    set_task_priority(t1["id"], "CRITICAL")
    assert t1["priority"] == "CRITICAL"

def test_invalid_priority():
    t = create_task("Test")
    with pytest.raises(ValueError, match="Invalid priority"):
        set_task_priority(t["id"], "SUPERHIGH")

def test_sort_by_priority():
    t1 = create_task("Critique", priority="CRITICAL")
    t2 = create_task("Haute", priority="HIGH")
    t3 = create_task("Normale")
    t4 = create_task("Basse", priority="LOW")
    sorted_tasks = get_tasks(sort_by="priority", order="asc")
    prios = [t["priority"] for t in sorted_tasks]
    assert prios == ["CRITICAL", "HIGH", "NORMAL", "LOW"]

def test_filter_by_priority():
    t1 = create_task("Normale")
    t2 = create_task("Haute", priority="HIGH")
    crit = get_tasks(priority="HIGH")
    assert len(crit) == 1 and crit[0]["title"] == "Haute"
