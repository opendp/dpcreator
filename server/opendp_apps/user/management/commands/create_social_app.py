import json

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from allauth.socialaccount.models import *


class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        filepath = 'google_account.json'
        with open(filepath, 'r') as infile:
            params = json.load(infile)
            Site.objects.all().delete()
            site, _ = Site.objects.get_or_create(domain='localhost:8000',
                                                 name='localhost',
                                                 id=3)

            social_app = SocialApp.objects.create(
                provider='google',
                name='google_auth',
                client_id=params['client_id'],
                secret=params['client_secret']
            )
            social_app.sites.add(site)
            print("provider: ", social_app.provider)
            print("name: ", social_app.name)
