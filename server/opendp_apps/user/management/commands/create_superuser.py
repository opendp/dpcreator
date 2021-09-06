from django.core.management.base import BaseCommand

from opendp_apps.user.models import OpenDPUser


class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        """Create a test superuser"""
        #OpenDPUser.objects.filter(is_superuser=True, username='admin').delete()
        params = dict(username='admin',
                      email='opendp_admin@some.edu',
                      first_name='Molly',
                      last_name='McNamara',
                      is_superuser=True,
                      is_staff=True)
        user, _created = OpenDPUser.objects.get_or_create(**params)
        user.set_password('admin')
        user.save()