"""
Set the specified RegisteredDataverse as active while marking any others as inactive
"""
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator

from opendp_apps.dataverses.models import RegisteredDataverse


class Command(BaseCommand):
    help = ("Create/set the specified RegisteredDataverse as active while marking"
            " any others as inactive."
            "\nExample usage:"
            " python manage.py set_registered_dataverse https://demo-dataverse.org \"Demo Dataverse\"")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('dataverse_url', type=str,
                            help=('URL of the RegisteredDataverse, including http/https.'
                                  ' Example: https://demo-dataverse.dpcreator.org'))
        parser.add_argument('name', type=str, help='Name of the RegisteredDataverse')

    def handle(self, *args, **options):
        """
        Set RegisteredDataverse. Convenience command for deploy updates
        Format: python manage.py set_registered_dataverse https://demo-dataverse.dpcreator.org|"Demo Dataverse"
        The arg
        """
        dataverse_url = options['dataverse_url']
        name = options['name']

        # Is the url valid?
        #
        url_validator = URLValidator()
        try:
            url_validator(dataverse_url)
        except ValidationError:
            user_msg = (f'This is not a valid dataverse_url: {dataverse_url}'
                        '\nPlease try again.')
            self.stdout.write(self.style.WARNING(user_msg))
            return

        # Set to lowercase, remove trailing slashes
        #
        dataverse_url = RegisteredDataverse.format_dv_url(dataverse_url)

        # Retrieve or create a new RegisteredDataverse
        #
        try:
            # Does a RegisteredDataverse already exist with this url?
            rd = RegisteredDataverse.objects.get(dataverse_url=dataverse_url)
            rd.name = name  # Use the updated name
        except RegisteredDataverse.DoesNotExist:
            # Existing RegisteredDataverse not found, create a new one
            rd = RegisteredDataverse(name=name, dataverse_url=dataverse_url)

        rd.active = True
        rd.save()

        # If there are other RegisteredDataverse objects, set them to inactive
        #
        user_msg = '>> Deactivate other RegisteredDataverse objects'
        self.stdout.write(self.style.SUCCESS(user_msg))
        cnt = 0
        for rd_to_deactivate in RegisteredDataverse.objects.exclude(object_id=rd.object_id):
            cnt += 1
            rd_to_deactivate.active = False
            rd_to_deactivate.save()

            user_msg = (f' - ({cnt}) INACTIVE:'
                        f'\n      - dataverse_url: {rd_to_deactivate.dataverse_url}'
                        f'\n      - name: {rd_to_deactivate.name}'
                        f'\n      - object_id: {rd_to_deactivate.object_id}')
            self.stdout.write(self.style.SUCCESS(user_msg))

        if cnt == 0:
            self.stdout.write(self.style.SUCCESS(' - (No RegisteredDataverse to deactivate.)'))

        user_msg = (f'\n>> Activate RegisteredDataverse:'
                    f'\n     - dataverse_url: {rd.dataverse_url}'
                    f'\n     - name: {rd.name}'
                    f'\n     - object_id: {rd.object_id}'
                    '\nSuccess!')
        self.stdout.write(self.style.SUCCESS(user_msg))

