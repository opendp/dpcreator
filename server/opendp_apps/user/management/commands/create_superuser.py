from django.core.management.base import BaseCommand

from opendp_apps.user.models import OpenDPUser


class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        OpenDPUser.objects.filter(is_superuser=True).delete()
        params = dict(username='admin',
                      email='admin@univ.org',
                      first_name='Molly',
                      last_name='McNamara',
                      is_superuser=True,
                      is_staff=True)
        user = OpenDPUser.objects.create(**params)
        user.set_password('admin')
        user.save()