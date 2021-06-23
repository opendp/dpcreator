#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():

    # use seperate settings.py for tests
    if 'test' in sys.argv:
        print('Using settings/development_test.py')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendp_project.settings.development_test')
    elif not 'DJANGO_SETTINGS_MODULE' in os.environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendp_project.settings.development')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
