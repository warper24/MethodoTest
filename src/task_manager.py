import json
import os
from typing import List, Dict, Union
from datetime import datetime

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

# On charge task_list UNE FOIS au lancement, puis on NE MODIFIE PLUS JAMAIS LE FICHIER
task_list: List[Dict] = _load_tasks()

def sort_tasks(tasks, sort_by="created_at", order="desc"):
    """
    Trie la liste de tâches selon le critère.
    - sort_by : 'created_at', 'title', 'status'
    - order : 'asc' (croissant) ou 'desc' (décroissant)
    - status : ordre logique = TODO, ONGOING, DONE
    Lève ValueError si critère invalide.
    """
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

def get_tasks(page=1, page_size=20, return_pagination=False, sort_by="created_at", order="desc"):
    """
    Récupère les tâches avec pagination et tri.
    - page: numéro de page (dès 1)
    - page_size: taille de page (>0)
    - return_pagination: si True, retourne aussi les infos de pagination
    - sort_by: champ de tri ('created_at', 'title', 'status')
    - order: 'asc' ou 'desc'
    """
    if page_size <= 0:
        raise ValueError("Invalid page size")
    sorted_tasks = sort_tasks(task_list, sort_by=sort_by, order=order)
    total_items = len(sorted_tasks)
    total_pages = (total_items + page_size - 1) // page_size if total_items else 0
    start = (page - 1) * page_size
    end = start + page_size
    paged_tasks = sorted_tasks[start:end]

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
    """
    Crée une nouvelle tâche :
    - title : chaîne non vide (max 100 caractères)
    - description : chaîne optionnelle (max 500 caractères)
    Retourne le dict de la tâche créée, avec :
    - id unique
    - status "TODO"
    - created_at : ISO string (à la seconde près)
    """
    # Nettoyage et validations
    title_stripped = title.strip()
    if not title_stripped:
        raise ValueError("Title is required")
    if len(title_stripped) > 100:
        raise ValueError("Title cannot exceed 100 characters")
    if len(description) > 500:
        raise ValueError("Description cannot exceed 500 characters")

    # Calcul du nouvel ID
    new_id = max((task["id"] for task in task_list), default=0) + 1

    # Création de la tâche
    new_task = {
        "id": new_id,
        "title": title_stripped,
        "description": description,
        "status": "TODO",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    # Ajout et persistance
    task_list.append(new_task)
    return new_task

def get_task(task_id: Union[int, str]) -> Dict:
    """
    Récupère les détails d'une tâche par son ID.
    - task_id peut être un int ou une str convertible en int.
    - lève ValueError("Invalid ID format") si format invalide.
    - lève ValueError("Task not found") si aucun ID correspondant.
    """
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")

    for task in task_list:
        if task.get("id") == tid:
            return task

    raise ValueError("Task not found")

def update_task(task_id, title=None, description=None):
    """
    Modifie le titre et/ou la description d'une tâche.
    - title: string (optionnel)
    - description: string (optionnel)
    - lève ValueError avec message approprié si problème (voir critères d'acceptation)
    """
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid ID format")
    for task in task_list:
        if task.get("id") == tid:
            # Gestion titre
            if title is not None:
                title_stripped = title.strip()
                if not title_stripped:
                    raise ValueError("Title is required")
                if len(title_stripped) > 100:
                    raise ValueError("Title cannot exceed 100 characters")
                task["title"] = title_stripped
            # Gestion description
            if description is not None:
                if len(description) > 500:
                    raise ValueError("Description cannot exceed 500 characters")
                task["description"] = description
            # Ignore les champs non modifiables
            return task
    raise ValueError("Task not found")

def change_task_status(task_id, status):
    """
    Change le statut d'une tâche.
    - status doit être 'TODO', 'ONGOING' ou 'DONE'
    """
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
    """
    Supprime une tâche existante.
    """
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
    Recherche les tâches par mot-clé dans le titre ou la description (insensible à la casse).
    Résultats paginés et triés.
    """
    if page_size <= 0:
        raise ValueError("Invalid page size")
    if keyword == "" or keyword is None:
        results = list(task_list)
    else:
        kw = keyword.lower()
        results = [
            task for task in task_list
            if kw in task.get("title", "").lower() or kw in task.get("description", "").lower()
        ]
    sorted_results = sort_tasks(results, sort_by=sort_by, order=order)
    start = (page - 1) * page_size
    end = start + page_size
    return sorted_results[start:end]

def filter_tasks_by_status(status, page=1, page_size=10, sort_by="created_at", order="desc"):
    """
    Filtre les tâches par statut ('TODO', 'ONGOING', 'DONE').
    Résultats paginés et triés. Lève ValueError si statut invalide.
    """
    allowed_status = {"TODO", "ONGOING", "DONE"}
    if status not in allowed_status:
        raise ValueError("Invalid filter status")
    if page_size <= 0:
        raise ValueError("Invalid page size")
    filtered = [task for task in task_list if task["status"] == status]
    sorted_filtered = sort_tasks(filtered, sort_by=sort_by, order=order)
    start = (page - 1) * page_size
    end = start + page_size
    return sorted_filtered[start:end]
