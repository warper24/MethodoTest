#!/usr/bin/env python3

import click
from rich.console import Console
from rich.table import Table

from task_manager import get_tasks

console = Console()

@click.group()
def cli():
    """Gestionnaire de Tâches - Version CLI Python"""
    pass

@cli.command()
@click.option("--sort-by", type=click.Choice(["created_at", "title", "status"]), default="created_at")
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1)
@click.option("--page-size", type=int, default=20)
def list(sort_by, order, page, page_size):
    """Lister les tâches triées et paginées"""
    try:
        tasks, pagination = get_tasks(
            page=page,
            page_size=page_size,
            return_pagination=True,
            sort_by=sort_by,
            order=order
        )
    except ValueError as e:
        console.print(str(e), style="bold red")
        return

    if not tasks:
        console.print("Aucune tâche trouvée.", style="yellow")
        return

    table = Table(title=f"Liste des tâches (tri {sort_by} {order}, page {page})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Statut", style="green")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Créée le", style="magenta")

    for task in tasks:
        table.add_row(
            str(task["id"]),
            task['status'],
            task["title"],
            task["description"],
            task["created_at"],
        )

    console.print(table)

@cli.command()
@click.argument("keyword", required=False, default="")
@click.option("--sort-by", type=click.Choice(["created_at", "title", "status"]), default="created_at")
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1, help="Numéro de page")
@click.option("--page-size", type=int, default=10, help="Taille de page")
def search(keyword, sort_by, order, page, page_size):
    """Recherche de tâches par mot-clé (titre ou description)"""
    try:
        results = get_tasks(
            keyword=keyword,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order
        )
    except ValueError as e:
        console.print(str(e), style="bold red")
        return

    if not results:
        console.print("Aucun résultat pour la recherche.", style="yellow")
        return

    table = Table(title=f"Résultats pour '{keyword}' (tri {sort_by} {order}, page {page})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Statut", style="green")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Créée le", style="magenta")

    for task in results:
        table.add_row(
            str(task["id"]),
            task['status'],
            task["title"],
            task["description"],
            task["created_at"],
        )

    console.print(table)

@cli.command()
@click.argument("status", required=True)
@click.option("--sort-by", type=click.Choice(["created_at", "title", "status"]), default="created_at")
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1, help="Numéro de page")
@click.option("--page-size", type=int, default=10, help="Taille de page")
def filter(status, sort_by, order, page, page_size):
    """Filtrer les tâches par statut (TODO, ONGOING, DONE)"""
    try:
        results = get_tasks(
            status=status,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order
        )
    except ValueError as e:
        console.print(str(e), style="bold red")
        return

    if not results:
        console.print("Aucun résultat pour ce statut.", style="yellow")
        return

    table = Table(title=f"Tâches statut '{status}' (tri {sort_by} {order}, page {page})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Statut", style="green")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Créée le", style="magenta")

    for task in results:
        table.add_row(
            str(task["id"]),
            task['status'],
            task["title"],
            task["description"],
            task["created_at"],
        )

    console.print(table)

if __name__ == '__main__':
    console.print("Gestionnaire de Tâches - Version CLI Python\n", style="bold blue")
    cli()
