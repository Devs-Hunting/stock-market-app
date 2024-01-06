import os
import subprocess
import sys
from functools import wraps


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw"):
            return
        signal_handler(*args, **kwargs)

    return wrapper


@disable_for_loaddata
def load_fixtures():
    """
    This script automates the process of loading fixtures into a Django project's database.

    Designed to work across Windows, Linux, and MacOS.
    """

    root_directory = os.path.dirname(os.getcwd())
    django_project_path = os.path.join(root_directory, "src", "psmproject")
    fixtures_directory = os.path.join(root_directory, "fixtures")

    if not os.path.exists(os.path.join(django_project_path, "manage.py")):
        print("manage.py not found in the expected location. Make sure the Django project path is correct.")
        exit(1)

    python_exe = "python"
    if sys.platform == "win32":
        python_exe = "py"
    elif sys.platform == "linux" or sys.platform == "darwin":
        python_exe = "python3"

    fixtures = []
    for dirpath, _, filenames in os.walk(fixtures_directory):
        for filename in [f for f in filenames if f.endswith(".json")]:
            fixtures.append(os.path.join(dirpath, filename))

    fixtures.sort()

    for fixture_path in fixtures:
        subprocess.call([python_exe, os.path.join(django_project_path, "manage.py"), "loaddata", "-i", fixture_path])
        print(f"Loaded fixture: {fixture_path}")


if __name__ == "__main__":
    load_fixtures()
