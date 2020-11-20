from django.core.management.base import BaseCommand

from opendp_apps.user.models import OpenDPUser


class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        OpenDPUser.objects.filter(is_superuser=True).delete()
        user = OpenDPUser.objects.create(username='admin', is_superuser=True, is_staff=True)
        user.set_password('admin')
        user.save()