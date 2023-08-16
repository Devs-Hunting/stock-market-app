import os
import sys


def remove_migrations_and_db():
    """
    This script automates the process of:
    1. Removing the SQLite database (if it exists).
    2. Deleting all migration files from every app inside the Django project (excluding __init__.py and __pycache__).

    Designed to work across Windows, Linux, and MacOS.
    """

    django_project_path = os.path.join(os.path.dirname(os.getcwd()), "src", "psmproject")

    if not os.path.exists(os.path.join(django_project_path, "manage.py")):
        print("manage.py not found in the expected location. Make sure the Django project path is correct.")
        sys.exit(1)

    db_path = os.path.join(django_project_path, "db.sqlite3")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("db.sqlite3 removed.")

    for root_dir, dirs, files in os.walk(django_project_path):
        if "migrations" in dirs:
            migration_dir = os.path.join(root_dir, "migrations")
            for filename in os.listdir(migration_dir):
                file_path = os.path.join(migration_dir, filename)
                if filename != "__init__.py" and filename != "__pycache__" and os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"Cleared migration files from {migration_dir}.")

    print("All migration files and database have been removed.")


if __name__ == "__main__":
    remove_migrations_and_db()
