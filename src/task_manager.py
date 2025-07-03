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
    valid_sort = {"created_at", "title", "status", "priority"}
    valid_order = {"asc", "desc"}
    if sort_by not in valid_sort:
        raise ValueError("Invalid sort criteria")
    if order not in valid_order:
        raise ValueError("Invalid sort order")

    reverse = (order == "desc")

    if sort_by == "status":
        # Ordre logique TODO < ONGOING < DONE
        status_order = {"TODO": 0, "ONGOING": 1, "DONE": 2}
        return sorted(tasks, key=lambda t: status_order.get(t.get("status"), 99), reverse=reverse)
    elif sort_by == "created_at":
        return sorted(tasks, key=lambda t: t.get("created_at", ""), reverse=reverse)
    elif sort_by == "title":
        return sorted(tasks, key=lambda t: t.get("title", "").lower(), reverse=reverse)
    elif sort_by == "priority":
        priority_order = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
        return sorted(tasks, key=lambda t: priority_order.get(t.get("priority", "NORMAL"), 99), reverse=reverse)
    else:
        raise ValueError("Invalid sort criteria")


def get_tasks(
    page=1,
    page_size=20,
    return_pagination=False,
    sort_by="created_at",
    order="desc",
    keyword=None,
    status=None,
    priority=None
):
    """
    Récupère la liste des tâches en appliquant optionnellement :
    - un filtre sur le statut
    - une recherche par mot-clé (titre ou description)
    - un tri (created_at, title, status, priority)
    - un filtre par priorité
    - une pagination

    :param page: Numéro de page (dès 1)
    :param page_size: Taille de la page (>0)
    :param return_pagination: Si True, retourne aussi les infos de pagination
    :param sort_by: Critère de tri ('created_at', 'title', 'status', 'priority')
    :param order: Sens du tri ('asc', 'desc')
    :param keyword: Mot-clé de recherche (titre ou description, insensible à la casse)
    :param status: Statut à filtrer ('TODO', 'ONGOING', 'DONE')
    :param priority: Priorité à filtrer ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')
    """
    if page_size <= 0:
        raise ValueError("Invalid page size")

    tasks = list(task_list)

    # Filtrage par statut
    if status is not None:
        allowed_status = {"TODO", "ONGOING", "DONE"}
        if status not in allowed_status:
            raise ValueError("Invalid filter status")
        tasks = [t for t in tasks if t.get("status") == status]

    # Filtrage par priorité
    if priority is not None:
        allowed_prio = {"LOW", "NORMAL", "HIGH", "CRITICAL"}
        prio = priority.upper()
        if prio not in allowed_prio:
            raise ValueError("Invalid priority. Allowed values: LOW, NORMAL, HIGH, CRITICAL")
        tasks = [t for t in tasks if t.get("priority", "NORMAL") == prio]

    # Recherche par mot-clé
    if keyword is not None and keyword != "":
        kw = keyword.lower()
        tasks = [
            t for t in tasks
            if kw in t.get("title", "").lower() or kw in t.get("description", "").lower()
        ]

    # Tri (accepte 'priority' en plus des autres)
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

def create_task(title: str, description: str = "", due_date: str = None, priority: str = "NORMAL") -> Dict:
    title_stripped = title.strip()
    if not title_stripped:
        raise ValueError("Title is required")
    if len(title_stripped) > 100:
        raise ValueError("Title cannot exceed 100 characters")
    if len(description) > 500:
        raise ValueError("Description cannot exceed 500 characters")
    allowed_priorities = {"LOW", "NORMAL", "HIGH", "CRITICAL"}
    prio = (priority or "NORMAL").upper()
    if prio not in allowed_priorities:
        raise ValueError("Invalid priority. Allowed values: LOW, NORMAL, HIGH, CRITICAL")
    # Gestion de due_date (échéance)
    if due_date is not None:
        try:
            due_dt = datetime.fromisoformat(due_date)
        except Exception:
            raise ValueError("Invalid date format")
        due_date = due_dt.isoformat(timespec='seconds')
    new_id = max((task["id"] for task in task_list), default=0) + 1
    new_task = {
        "id": new_id,
        "title": title_stripped,
        "description": description,
        "status": "TODO",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "due_date": due_date,
        "priority": prio
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

def get_tasks_by_user(
    user_id=None,
    page=1,
    page_size=20,
    status=None,
    keyword=None,
    sort_by="created_at",
    order="desc",
    return_pagination=False
):
    """
    Retourne les tâches filtrées par assignation à un utilisateur donné (ou non assignées).
    - user_id : int, id de l'utilisateur ou None pour tâches non assignées
    - Les autres paramètres sont comme get_tasks
    """
    # Vérification de l'utilisateur si l'ID n'est pas None
    if user_id is not None:
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid user ID format")
        users = _load_users()
        if not any(u.get("id") == uid for u in users):
            raise ValueError("User not found")
    else:
        uid = None

    # Filtrage par assigné
    def assigned_filter(t):
        if uid is None:
            return t.get("assignee_id") is None
        else:
            return t.get("assignee_id") == uid

    tasks = [t for t in task_list if assigned_filter(t)]

    # Appliquer autres filtres (statut, mot-clé)
    if status is not None:
        allowed_status = {"TODO", "ONGOING", "DONE"}
        if status not in allowed_status:
            raise ValueError("Invalid filter status")
        tasks = [t for t in tasks if t["status"] == status]

    if keyword is not None and keyword != "":
        kw = keyword.lower()
        tasks = [
            t for t in tasks
            if kw in t.get("title", "").lower() or kw in t.get("description", "").lower()
        ]

    # Tri et pagination
    tasks = sort_tasks(tasks, sort_by=sort_by, order=order)
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
    
def set_due_date(task_id, due_date):
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for task in task_list:
        if task.get("id") == tid:
            if due_date is None:
                task["due_date"] = None
                return task
            try:
                from datetime import datetime
                due_dt = datetime.fromisoformat(due_date)
            except Exception:
                raise ValueError("Invalid date format")
            task["due_date"] = due_dt.isoformat(timespec='seconds')
            if due_dt < datetime.now():
                print("Warning: Due date is in the past")
            return task
    raise ValueError("Task not found")

def set_task_priority(task_id, priority):
    allowed = {"LOW", "NORMAL", "HIGH", "CRITICAL"}
    prio = (priority or "NORMAL").upper()
    if prio not in allowed:
        raise ValueError("Invalid priority. Allowed values: LOW, NORMAL, HIGH, CRITICAL")
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for task in task_list:
        if task.get("id") == tid:
            task["priority"] = prio
            return task
    raise ValueError("Task not found")

def is_overdue(task):
    """
    Retourne True si la tâche est en retard :
    - due_date est une chaîne 'YYYY-MM-DD' ou 'YYYY-MM-DDTHH:MM:SS'
    - on compare uniquement la DATE d'échéance et la DATE du jour courant
    - on marque en retard seulement si today > due_date
    - uniquement pour les statuts TODO ou ONGOING
    """
    from datetime import datetime

    due_str = task.get("due_date")
    if not due_str:
        return False

    try:
        # Si format complet avec 'T', on parse en datetime puis on prend la date
        if "T" in due_str:
            due_date = datetime.fromisoformat(due_str).date()
        else:
            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
    except Exception:
        # en cas de format invalide, on considère que ce n'est pas en retard
        return False

    today = datetime.now().date()
    if today > due_date and task.get("status") in ("TODO", "ONGOING"):
        return True
    return False

def get_overdue_tasks():
    """
    Renvoie la liste des tâches en retard selon is_overdue().
    """
    return [t for t in task_list if is_overdue(t)]


def add_tag(task_id, tag):
    tag = tag.strip()
    if not tag or len(tag) > 20:
        raise ValueError("Invalid tag validation")
    for task in task_list:
        if task.get("id") == int(task_id):
            tags = set(task.get("tags", []))
            tags.add(tag)
            task["tags"] = list(tags)
            return task
    raise ValueError("Task not found")

def add_tags(task_id, tags_list):
    for tag in tags_list:
        add_tag(task_id, tag)
    return get_task(task_id)

def remove_tag(task_id, tag):
    for task in task_list:
        if task.get("id") == int(task_id):
            tags = set(task.get("tags", []))
            tags.discard(tag)
            task["tags"] = list(tags)
            return task
    raise ValueError("Task not found")

def get_tasks_by_tag(tag):
    return [t for t in task_list if tag in t.get("tags", [])]

def get_tasks_by_tags(tags):
    tags_set = set(tags)
    return [t for t in task_list if tags_set.intersection(set(t.get("tags", [])))]

def get_all_tags():
    tags = {}
    for t in task_list:
        for tag in t.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    return tags
