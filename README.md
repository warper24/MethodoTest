# Task Manager - Version Python CLI

Gestionnaire de tâches minimal développé avec approche TDD en utilisant pytest.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Démarrer l'application CLI
```bash
python src/main.py --help
```

### Lancer les tests
```bash
# Tests simples
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests en mode verbose
pytest -v

# Tests avec monitoring des modifications
pytest-watch
```

## Couverture de tests

Objectif : maintenir une couverture > 90% sur la logique métier.

```bash
pytest --cov=src --cov-report=term-missing
```
### Recherche de tâches

- Recherche CLI : `python main.py search "motclef"`
- Options : `--page`, `--page-size`
- Recherche insensible à la casse, dans le titre et la description, paginée.

### Filtrer par statut

- Filtrer en CLI : `python main.py filter TODO`
- Options : `--page`, `--page-size`
- Statuts : TODO, ONGOING, DONE

### Tri des tâches

- Toutes les commandes supportent `--sort-by` (`created_at`, `title`, `status`) et `--order` (`asc`, `desc`)
- Ex: `python main.py list --sort-by title --order asc`
