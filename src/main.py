#!/usr/bin/env python3

import click
from rich.console import Console
from rich.table import Table
from datetime import datetime

from task_manager import (
    # Tâches
    get_tasks, create_task, get_task, update_task, change_task_status,
    delete_task, search_tasks, filter_tasks_by_status, assign_task,
    get_tasks_by_user, get_overdue_tasks, set_due_date, set_task_priority,
    add_tag, remove_tag, get_tasks_by_tag, get_all_tags,
    # Utilisateurs
    create_user, get_users
)

console = Console()


def _print_tasks(tasks, title):
    """Helper to render a list of tasks in a Rich table."""
    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Statut", style="green")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Créée le", style="magenta")
    table.add_column("Echéance", style="yellow")
    table.add_column("Priorité", style="red")
    table.add_column("Tags", style="blue")
    for t in tasks:
        table.add_row(
            str(t["id"]),
            t["status"],
            t["title"],
            t["description"] or "–",
            t["created_at"],
            t.get("due_date") or "–",
            t.get("priority", "NORMAL"),
            ", ".join(t.get("tags", [])) or "–"
        )
    console.print(table)


@click.group()
def cli():
    """Gestionnaire de Tâches - Version CLI Python"""
    pass


#
# --- TÂCHES ---
#

@cli.command()
@click.option("--sort-by", type=click.Choice(["created_at", "title", "status", "priority"]), default="created_at")
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=20)
def list(sort_by, order, page, page_size):
    """Lister toutes les tâches avec tri et pagination"""
    try:
        tasks, pag = get_tasks(
            page=page, page_size=page_size, return_pagination=True,
            sort_by=sort_by, order=order
        )
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    if not tasks:
        console.print("Aucune tâche à afficher.", style="yellow")
        return
    title = f"Tâches (page {pag['current_page']}/{pag['total_pages']}, tri {sort_by} {order})"
    _print_tasks(tasks, title)


@cli.command()
@click.argument("title")
@click.option("--description", default="", help="Description optionnelle")
@click.option("--due-date", default=None, help="Échéance au format YYYY-MM-DD ou ISO")
@click.option("--priority", type=click.Choice(["LOW","NORMAL","HIGH","CRITICAL"]), default="NORMAL")
def create(title, description, due_date, priority):
    """Créer une nouvelle tâche"""
    try:
        t = create_task(title, description=description, due_date=due_date, priority=priority)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Tâche créée (ID {t['id']})", style="green")


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", help="Nouveau titre")
@click.option("--description", help="Nouvelle description")
def update(task_id, title, description):
    """Mettre à jour titre et/ou description d'une tâche"""
    try:
        t = update_task(task_id, title=title, description=description)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Tâche {task_id} mise à jour.", style="green")


@cli.command(name="status")
@click.argument("task_id", type=int)
@click.argument("status", type=click.Choice(["TODO","ONGOING","DONE"]))
def status_cmd(task_id, status):
    """Changer le statut d'une tâche"""
    try:
        t = change_task_status(task_id, status)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Statut de la tâche {task_id} → {status}", style="green")


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id):
    """Supprimer une tâche"""
    try:
        delete_task(task_id)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Tâche {task_id} supprimée.", style="green")


@cli.command()
@click.argument("keyword", required=False, default="")
@click.option("--sort-by", type=click.Choice(["created_at","title","status","priority"]), default="created_at")
@click.option("--order", type=click.Choice(["asc","desc"]), default="desc")
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=10)
def search(keyword, sort_by, order, page, page_size):
    """Rechercher des tâches par mot-clé"""
    try:
        tasks = search_tasks(keyword, page=page, page_size=page_size, sort_by=sort_by, order=order)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    if not tasks:
        console.print(f"Aucun résultat pour '{keyword}'.", style="yellow")
        return
    _print_tasks(tasks, f"Résultats pour '{keyword}'")


@cli.command()
@click.argument("status", type=click.Choice(["TODO","ONGOING","DONE"]))
@click.option("--sort-by", type=click.Choice(["created_at","title","status","priority"]), default="created_at")
@click.option("--order", type=click.Choice(["asc","desc"]), default="desc")
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=10)
def filter(status, sort_by, order, page, page_size):
    """Filtrer les tâches par statut"""
    try:
        tasks = filter_tasks_by_status(status, page=page, page_size=page_size, sort_by=sort_by, order=order)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    if not tasks:
        console.print(f"Aucune tâche au statut {status}.", style="yellow")
        return
    _print_tasks(tasks, f"Tâches statut {status}")


@cli.command()
@click.argument("user_id", type=int, required=False)
@click.option("--sort-by", type=click.Choice(["created_at","title","status","priority"]), default="created_at")
@click.option("--order", type=click.Choice(["asc","desc"]), default="desc")
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=10)
def by_user(user_id, sort_by, order, page, page_size):
    """Lister tâches assignées à un utilisateur (ou non assignées si omis)"""
    try:
        tasks = get_tasks_by_user(user_id, page=page, page_size=page_size, sort_by=sort_by, order=order)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    header = f"Tâches pour user {user_id}" if user_id else "Tâches non assignées"
    _print_tasks(tasks, header)


@cli.command()
def overdue():
    """Lister les tâches en retard"""
    tasks = get_overdue_tasks()
    if not tasks:
        console.print("Aucune tâche en retard.", style="green")
        return
    _print_tasks(tasks, "Tâches en retard")


@cli.command()
@click.argument("task_id", type=int)
@click.argument("user_id", type=int, required=False)
def assign(task_id, user_id):
    """Assigner ou désassigner une tâche à un utilisateur"""
    try:
        t = assign_task(task_id, user_id)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    state = f"assignée à {user_id}" if user_id else "désassignée"
    console.print(f"Tâche {task_id} {state}.", style="green")


@cli.command()
@click.argument("task_id", type=int)
@click.argument("due_date", required=False)
def due(task_id, due_date):
    """Définir ou supprimer l’échéance d’une tâche"""
    try:
        t = set_due_date(task_id, due_date)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Échéance de la tâche {task_id} → {t.get('due_date')}", style="green")


@cli.command()
@click.argument("task_id", type=int)
@click.argument("priority", type=click.Choice(["LOW","NORMAL","HIGH","CRITICAL"]))
def priority(task_id, priority):
    """Définir ou modifier la priorité d’une tâche"""
    try:
        t = set_task_priority(task_id, priority)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Priorité de la tâche {task_id} → {t['priority']}", style="green")


@cli.command()
@click.argument("task_id", type=int)
@click.argument("tag")
def addtag(task_id, tag):
    """Ajouter un tag à une tâche"""
    try:
        t = add_tag(task_id, tag)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Tag '{tag}' ajouté à la tâche {task_id}.", style="green")


@cli.command()
@click.argument("task_id", type=int)
@click.argument("tag")
def rmtag(task_id, tag):
    """Retirer un tag d’une tâche"""
    try:
        t = remove_tag(task_id, tag)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Tag '{tag}' retiré de la tâche {task_id}.", style="green")


@cli.command()
@click.argument("tag")
def by_tag(tag):
    """Lister les tâches possédant un tag donné"""
    tasks = get_tasks_by_tag(tag)
    if not tasks:
        console.print(f"Aucune tâche avec le tag '{tag}'.", style="yellow")
        return
    _print_tasks(tasks, f"Tâches taggées '{tag}'")


@cli.command()
def tags():
    """Afficher tous les tags et leur fréquence"""
    freq = get_all_tags()
    if not freq:
        console.print("Aucun tag défini.", style="yellow")
        return
    table = Table(title="Tags disponibles")
    table.add_column("Tag", style="blue")
    table.add_column("Utilisations", style="cyan")
    for tag, count in sorted(freq.items(), key=lambda x: x[0]):
        table.add_row(tag, str(count))
    console.print(table)


#
# --- UTILISATEURS ---
#

@cli.command()
@click.argument("name")
@click.argument("email")
def new_user(name, email):
    """Créer un nouvel utilisateur"""
    try:
        u = create_user(name, email)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return
    console.print(f"Utilisateur créé (ID {u['id']})", style="green")


@cli.command()
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=20)
def users(page, page_size):
    """Lister les utilisateurs"""
    users, pag = get_users(page=page, page_size=page_size, return_pagination=True)
    if not users:
        console.print("Aucun utilisateur.", style="yellow")
        return
    table = Table(title=f"Utilisateurs (page {pag['current_page']}/{pag['total_pages']})")
    table.add_column("ID", style="cyan")
    table.add_column("Nom", style="white")
    table.add_column("Email", style="green")
    table.add_column("Créé le", style="magenta")
    for u in users:
        table.add_row(str(u["id"]), u["name"], u["email"], u["created_at"])
    console.print(table)


if __name__ == '__main__':
    console.print("Gestionnaire de Tâches - Version CLI Python\n", style="bold blue")
    cli()
