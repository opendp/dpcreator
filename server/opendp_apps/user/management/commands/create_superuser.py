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
        self.stdout.write(self.style.WARNING('>> Preparing to create superuser'))

        username = 'dev_admin'

        opendp_user = OpenDPUser.objects.filter(username=username).first()
        if opendp_user and not opendp_user.is_superuser:
            user_msg = (f'>> An OpenDPUser with username "{username}" exists. '
                        f'\n>> But this user is NOT a superuser')
            self.stdout.write(self.style.ERROR(user_msg))
            return

        if opendp_user:
            user_msg = f'>> An OpenDPUser with username "{username}" exists'
            self.write_success_msg(user_msg)
        else:
            params = dict(username=username,
                      email='opendp_admin@some.edu',
                      first_name='Molly',
                      last_name='McNamara',
                      is_superuser=True,
                      is_staff=True)
            opendp_user, _created = OpenDPUser.objects.get_or_create(**params)
            self.write_success_msg(f'>> superuser created: {opendp_user.username}')

        if opendp_user.check_password(_ADMIN_PASSWORD):
            self.write_success_msg(f'>> password looks good for: {opendp_user.username}')
        else:
            opendp_user.set_password(_ADMIN_PASSWORD)
            opendp_user.save()
            self.write_success_msg(f'>> password updated for: {opendp_user.username}')

    def write_success_msg(self, user_msg: str, indent=True):
        """Print output statement"""
        if indent:
            user_msg = f'  - {user_msg}'
        self.stdout.write(self.style.SUCCESS(user_msg))