import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs the tests.py script"

    def handle(self, *args, **kwargs):
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        script_path = os.path.join(project_root, "tests.py")
        try:
            with open(script_path) as f:
                code = f.read()
                exec(code)
        except FileNotFoundError:
            self.stderr.write(f"File not found: {script_path}")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
