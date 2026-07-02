#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import warnings
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Suppress deprecation warnings (optional)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Set the default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Add custom management commands path
    # This allows running python manage.py <custom_command>
    from django.core.management import find_commands, load_command_class
    
    # Execute the command
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()