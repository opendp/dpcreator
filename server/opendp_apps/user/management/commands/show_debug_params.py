import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """

    def show_dir_contents(self, name_of_dir, level=None):
        if not level:
            level = 1
        if os.path.exists(name_of_dir):
            print('-' * 40)
            print(f' >> {name_of_dir}')
            print('-' * 40)
            for af in os.listdir(name_of_dir):
                print(f'({level}) entry: ', af)
                if af in ('static', 'dist', 'js'):
                    self.show_dir_contents(os.path.join(name_of_dir, af), level=level + 1)
                    print('-- End level:', level + 1)
                    print('-' * 40)

    def handle(self, *args, **options):
        print('USE_DEV_STATIC_SERVER', settings.USE_DEV_STATIC_SERVER)
        print('BASE_DIR', settings.BASE_DIR)
        print('STATIC_ROOT', settings.STATIC_ROOT)
        # self.show_dir_contents(settings.STATIC_ROOT)
