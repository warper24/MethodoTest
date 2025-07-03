import json
import os
from typing import List, Dict, Union
from datetime import datetime
import re

DATA_FILE = "tasks.json"

def _load_tasks():
    """Charge une seule fois les tâches depuis le fichier JSON, ne jamais écrire dans ce fichier."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    # Fallback minimal si problème :
    return [
        {"id": 1, "title": "Première tâche", "description": "Description de la première tâche", "status": "TODO", "created_at": datetime.now().isoformat(timespec="seconds")},
        {"id": 2, "title": "Deuxième tâche", "description": "Description de la deuxième tâche", "status": "DONE", "created_at": datetime.now().isoformat(timespec="seconds")}
    ]

USERS_FILE = "users.json"

def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


# On charge task_list UNE FOIS au lancement, puis on NE MODIFIE PLUS JAMAIS LE FICHIER
task_list: List[Dict] = _load_tasks()

def sort_tasks(tasks, sort_by="created_at", order="desc"):
    valid_sort = {"created_at", "title", "status"}
    valid_order = {"asc", "desc"}
    if sort_by not in valid_sort:
        raise ValueError("Invalid sort criteria")
    if order not in valid_order:
        raise ValueError("Invalid sort order")

    reverse = (order == "desc")

    if sort_by == "status":
        # Ordre logique TODO < ONGOING < DONE
        status_order = {"TODO": 0, "ONGOING": 1, "DONE": 2}
        return sorted(tasks, key=lambda t: status_order.get(t["status"], 99))
    elif sort_by == "created_at":
        return sorted(tasks, key=lambda t: t["created_at"], reverse=reverse)
    elif sort_by == "title":
        return sorted(tasks, key=lambda t: t["title"].lower(), reverse=reverse)
    else:
        raise ValueError("Invalid sort criteria")

def get_tasks(
    page=1,
    page_size=20,
    return_pagination=False,
    sort_by="created_at",
    order="desc",
    keyword=None,
    status=None
):
    """
    Récupère la liste des tâches en appliquant optionnellement :
    - un filtre sur le statut
    - une recherche par mot-clé (titre ou description)
    - un tri (created_at, title, status)
    - une pagination

    :param page: Numéro de page (dès 1)
    :param page_size: Taille de la page (>0)
    :param return_pagination: Si True, retourne aussi les infos de pagination
    :param sort_by: Critère de tri ('created_at', 'title', 'status')
    :param order: Sens du tri ('asc', 'desc')
    :param keyword: Mot-clé de recherche (titre ou description, insensible à la casse)
    :param status: Statut à filtrer ('TODO', 'ONGOING', 'DONE')
    """
    if page_size <= 0:
        raise ValueError("Invalid page size")

    tasks = list(task_list)

    # Filtrage par statut
    if status is not None:
        allowed_status = {"TODO", "ONGOING", "DONE"}
        if status not in allowed_status:
            raise ValueError("Invalid filter status")
        tasks = [t for t in tasks if t["status"] == status]

    # Recherche par mot-clé
    if keyword is not None and keyword != "":
        kw = keyword.lower()
        tasks = [
            t for t in tasks
            if kw in t.get("title", "").lower() or kw in t.get("description", "").lower()
        ]

    # Tri
    tasks = sort_tasks(tasks, sort_by=sort_by, order=order)

    # Pagination
    total_items = len(tasks)
    total_pages = (total_items + page_size - 1) // page_size if total_items else 0
    start = (page - 1) * page_size
    end = start + page_size
    paged_tasks = tasks[start:end]

    if return_pagination:
        pagination = {
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_items": total_items
        }
        return paged_tasks, pagination
    else:
        return paged_tasks

def create_task(title: str, description: str = "") -> Dict:
    title_stripped = title.strip()
    if not title_stripped:
        raise ValueError("Title is required")
    if len(title_stripped) > 100:
        raise ValueError("Title cannot exceed 100 characters")
    if len(description) > 500:
        raise ValueError("Description cannot exceed 500 characters")

    new_id = max((task["id"] for task in task_list), default=0) + 1

    new_task = {
        "id": new_id,
        "title": title_stripped,
        "description": description,
        "status": "TODO",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }
    task_list.append(new_task)
    return new_task

def get_task(task_id: Union[int, str]) -> Dict:
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")

    for task in task_list:
        if task.get("id") == tid:
            return task

    raise ValueError("Task not found")

def update_task(task_id, title=None, description=None):
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for task in task_list:
        if task.get("id") == tid:
            if title is not None:
                title_stripped = title.strip()
                if not title_stripped:
                    raise ValueError("Title is required")
                if len(title_stripped) > 100:
                    raise ValueError("Title cannot exceed 100 characters")
                task["title"] = title_stripped
            if description is not None:
                if len(description) > 500:
                    raise ValueError("Description cannot exceed 500 characters")
                task["description"] = description
            return task
    raise ValueError("Task not found")

def change_task_status(task_id, status):
    allowed = {"TODO", "ONGOING", "DONE"}
    if status not in allowed:
        raise ValueError("Invalid status. Allowed values: TODO, ONGOING, DONE")
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for task in task_list:
        if task.get("id") == tid:
            task["status"] = status
            return task
    raise ValueError("Task not found")

def delete_task(task_id):
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for i, task in enumerate(task_list):
        if task.get("id") == tid:
            del task_list[i]
            return
    raise ValueError("Task not found")

def search_tasks(keyword, page=1, page_size=10, sort_by="created_at", order="desc"):
    """
    Recherche les tâches par mot-clé dans le titre ou la description.
    Utilise get_tasks pour centraliser la logique.
    """
    return get_tasks(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        keyword=keyword
    )

def filter_tasks_by_status(status, page=1, page_size=10, sort_by="created_at", order="desc"):
    """
    Filtre les tâches par statut.
    Utilise get_tasks pour centraliser la logique.
    """
    return get_tasks(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        status=status
    )

def assign_task(task_id: Union[int, str], user_id: Union[int, str, None]):
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid task ID format")

    if user_id is not None:
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid user ID format")

        user_found = any(u.get("id") == uid for u in _load_users())
        if not user_found:
            raise ValueError("User not found")
    else:
        uid = None  # désassignation

    for task in task_list:
        if task.get("id") == tid:
            task["assignee_id"] = uid
            return task

    raise ValueError("Task not found")

USERS_FILE = "users.json"

def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []

def _save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except IOError:
        pass

def create_user(name: str, email: str) -> dict:
    name_stripped = name.strip()
    if not name_stripped:
        raise ValueError("Name is required")
    if len(name_stripped) > 50:
        raise ValueError("Name cannot exceed 50 characters")

    email = email.strip().lower()
    # Validation très simple d'email
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        raise ValueError("Invalid email format")
    
    users = _load_users()
    for user in users:
        if user["email"].lower() == email:
            raise ValueError("Email already in use")

    new_id = max([u["id"] for u in users], default=0) + 1
    from datetime import datetime
    user = {
        "id": new_id,
        "name": name_stripped,
        "email": email,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }
    users.append(user)
    _save_users(users)
    return user

def get_users(page=1, page_size=20, return_pagination=False):
    """
    Retourne la liste paginée et triée (par nom) des utilisateurs.
    """
    users = _load_users()
    users = sorted(users, key=lambda u: u["name"].lower())
    total_items = len(users)
    total_pages = (total_items + page_size - 1) // page_size if total_items else 0
    start = (page - 1) * page_size
    end = start + page_size
    paged_users = users[start:end]
    if return_pagination:
        pagination = {
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_items": total_items
        }
        return paged_users, pagination
    else:
        return paged_users
