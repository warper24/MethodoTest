from src.task_manager import create_user, get_users
import os
import json
import pytest

def setup_function(function):
    # Vide le fichier users.json avant chaque test
    if os.path.exists("users.json"):
        os.remove("users.json")

def test_create_user_success():
    user = create_user("Jean", "jean@example.com")
    assert user["id"] == 1
    assert user["name"] == "Jean"
    assert user["email"] == "jean@example.com"
    assert "created_at" in user

def test_create_user_trims_name_and_email():
    user = create_user("   Pierre   ", "   pierre@example.com  ")
    assert user["name"] == "Pierre"
    assert user["email"] == "pierre@example.com"

def test_create_user_duplicate_email():
    create_user("Alice", "alice@example.com")
    with pytest.raises(ValueError, match="Email already in use"):
        create_user("Bob", "alice@example.com")

def test_create_user_invalid_email_format():
    with pytest.raises(ValueError, match="Invalid email format"):
        create_user("Sam", "notanemail")

def test_create_user_empty_name():
    with pytest.raises(ValueError, match="Name is required"):
        create_user("   ", "a@b.com")

def test_create_user_too_long_name():
    long_name = "A" * 51
    with pytest.raises(ValueError, match="Name cannot exceed 50 characters"):
        create_user(long_name, "troplong@example.com")

def setup_function(function):
    if os.path.exists("users.json"):
        os.remove("users.json")

def test_get_users_returns_all_users_sorted():
    create_user("Charlie", "c@example.com")
    create_user("Alice", "a@example.com")
    create_user("Bob", "b@example.com")
    users = get_users()
    names = [u["name"] for u in users]
    assert names == ["Alice", "Bob", "Charlie"]

def test_get_users_empty_returns_empty_list():
    users = get_users()
    assert users == []

def test_get_users_with_pagination():
    # Crée 5 utilisateurs
    for i in range(1, 6):
        create_user(f"User{i}", f"user{i}@example.com")
    # Page 1 (taille 2)
    users = get_users(page=1, page_size=2)
    assert len(users) == 2
    # Page 2 (taille 2)
    users = get_users(page=2, page_size=2)
    assert len(users) == 2
    # Page 3 (taille 2) -> reste 1 utilisateur
    users = get_users(page=3, page_size=2)
    assert len(users) == 1

def test_get_users_return_pagination_info():
    for i in range(6):
        create_user(f"Name{i}", f"name{i}@example.com")
    users, pagination = get_users(page=2, page_size=2, return_pagination=True)
    assert pagination["current_page"] == 2
    assert pagination["page_size"] == 2
    assert pagination["total_items"] == 6
    assert pagination["total_pages"] == 3