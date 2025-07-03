import pytest
from src.task_manager import create_task, add_tag, add_tags, remove_tag, get_tasks_by_tag, get_tasks_by_tags, get_all_tags, task_list

def setup_function(function):
    task_list.clear()

def test_add_tag_ok():
    t = create_task("T1")
    add_tag(t["id"], "projet")
    assert "projet" in t["tags"]

def test_add_tag_too_long():
    t = create_task("T2")
    with pytest.raises(ValueError, match="Invalid tag validation"):
        add_tag(t["id"], "t" * 21)

def test_add_tag_empty():
    t = create_task("T3")
    with pytest.raises(ValueError, match="Invalid tag validation"):
        add_tag(t["id"], "")

def test_add_multiple_tags():
    t = create_task("T4")
    add_tags(t["id"], ["alpha", "beta"])
    assert set(t["tags"]) == {"alpha", "beta"}

def test_remove_tag():
    t = create_task("T5")
    add_tags(t["id"], ["x", "y"])
    remove_tag(t["id"], "x")
    assert "x" not in t["tags"]
    assert "y" in t["tags"]

def test_get_tasks_by_tag():
    t1 = create_task("A")
    t2 = create_task("B")
    add_tag(t1["id"], "team")
    add_tag(t2["id"], "team")
    result = get_tasks_by_tag("team")
    assert t1 in result and t2 in result

def test_get_tasks_by_tags():
    t1 = create_task("A")
    t2 = create_task("B")
    t3 = create_task("C")
    add_tags(t1["id"], ["x", "y"])
    add_tags(t2["id"], ["y"])
    add_tags(t3["id"], ["z"])
    found = get_tasks_by_tags(["x", "z"])
    assert t1 in found and t3 in found and t2 not in found

def test_get_all_tags():
    t1 = create_task("A")
    t2 = create_task("B")
    add_tags(t1["id"], ["a", "b"])
    add_tags(t2["id"], ["b", "c"])
    tag_dict = get_all_tags()
    assert tag_dict == {"a": 1, "b": 2, "c": 1}
