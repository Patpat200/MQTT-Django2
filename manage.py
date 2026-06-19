#!/usr/bin/env python
"""Utilitaire Django en ligne de commande (administration du projet)."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. As-tu activé ton environnement "
            "virtuel (venv) et installé les dépendances ?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
