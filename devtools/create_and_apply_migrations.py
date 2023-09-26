import os
import subprocess
import sys


def create_and_apply_migrations():
    """
    This script automates the process of:
    1. Creating new migrations for all apps in a Django project.
    2. Applying these migrations to the database.

    Designed to work across Windows, Linux, and MacOS.
    """

    django_project_path = os.path.join(os.path.dirname(os.getcwd()), "src", "psmproject")

    if not os.path.exists(os.path.join(django_project_path, "manage.py")):
        print("manage.py not found in the expected location. Make sure the Django project path is correct.")
        exit(1)

    python_exe = "python"
    if sys.platform == "win32":
        python_exe = "py"
    elif sys.platform == "linux" or sys.platform == "darwin":
        python_exe = "python3"

    def run_manage_command(command):
        subprocess.call([python_exe, os.path.join(django_project_path, "manage.py"), command])

    run_manage_command("makemigrations")
    run_manage_command("migrate")
    print("Migrations have been created and applied.")


if __name__ == "__main__":
    create_and_apply_migrations()
