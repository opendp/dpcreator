import os

from django.core.management.base import BaseCommand

from opendp_apps.user.models import OpenDPUser

_ADMIN_PASSWORD = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin')

class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        """Create a test superuser"""
        username = 'dev_admin'

        if OpenDPUser.objects.filter(username=username).exists():
            user_msg = f'>> An OpenDPUser with username "{username}" already exists'
            self.stdout.write(self.style.ERROR(user_msg))
            return

        params = dict(username=username,
                      email='opendp_admin@some.edu',
                      first_name='Molly',
                      last_name='McNamara',
                      is_superuser=True,
                      is_staff=True)
        user, _created = OpenDPUser.objects.get_or_create(**params)

        user.set_password(_ADMIN_PASSWORD)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'>> superuser created: {user.username}'))
