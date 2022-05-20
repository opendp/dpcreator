"""
Usage at top of other scripts_dev

from load_django_settings import load_local_settings
load_local_settings()
"""
import os
import sys
from os.path import abspath, dirname, join

CURRENT_DIR = dirname(abspath(__file__))
SERVER_DIR = dirname(CURRENT_DIR)
TEST_DATA_DIR = join(SERVER_DIR, 'test_data')
PROJECT_DIR = dirname(SERVER_DIR)

sys.path.append(CURRENT_DIR)
sys.path.append(SERVER_DIR)  # server dir


def load_local_settings():
    if not 'DJANGO_SETTINGS_MODULE' in os.environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                              'opendp_project.settings.cypress_settings')
        # 'opendp_project.settings.development')

    import django
    try:
        django.setup()
    except Exception as e:
        print("WARNING: Can't configure Django. %s" % e)


if __name__ == '__main__':
    load_local_settings()
