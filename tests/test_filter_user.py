from src.task_manager import get_tasks_by_user, assign_task, create_task, task_list, _save_users, _load_users
import pytest
import os
import json

def setup_module(module):
    # Prépare des users et des tâches pour tous les tests de ce module
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2025-07-01T12:00:00"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "created_at": "2025-07-01T12:01:00"}
    ]
    _save_users(users)
    task_list.clear()
    # Tâche assignée à Alice
    t1 = create_task("Pour Alice", "desc1")
    assign_task(t1["id"], 1)
    # Tâche assignée à Bob
    t2 = create_task("Pour Bob", "desc2")
    assign_task(t2["id"], 2)
    # Tâche non assignée
    t3 = create_task("Non assignée", "desc3")
    # Tâche assignée à Alice, status DONE
    t4 = create_task("Terminé Alice", "desc4")
    assign_task(t4["id"], 1)
    t4["status"] = "DONE"

def test_filter_tasks_by_user_alice():
    tasks = get_tasks_by_user(user_id=1)
    assert all(t.get("assignee_id") == 1 for t in tasks)
    assert len(tasks) == 2

def test_filter_tasks_by_user_bob():
    tasks = get_tasks_by_user(user_id=2)
    assert all(t.get("assignee_id") == 2 for t in tasks)
    assert len(tasks) == 1

def test_filter_tasks_by_unassigned():
    tasks = get_tasks_by_user(user_id=None)
    assert all(t.get("assignee_id") is None for t in tasks)
    assert len(tasks) == 1

def test_filter_by_user_with_no_tasks():
    # Ajoute un nouvel utilisateur sans tâches assignées
    users = [
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "created_at": "2025-07-01T12:02:00"}
    ]
    _save_users(_load_users() + users)
    tasks = get_tasks_by_user(user_id=3)
    assert tasks == []

def test_filter_by_nonexistent_user():
    with pytest.raises(ValueError, match="User not found"):
        get_tasks_by_user(user_id=999)

def test_filter_by_user_and_status():
    # Pour Alice avec statut "DONE"
    tasks = get_tasks_by_user(user_id=1, status="DONE")
    assert all(t.get("assignee_id") == 1 and t["status"] == "DONE" for t in tasks)
    assert len(tasks) == 1

def test_filter_by_user_and_keyword():
    tasks = get_tasks_by_user(user_id=1, keyword="Terminé")
    assert all(t.get("assignee_id") == 1 and "Terminé" in t["title"] for t in tasks)
