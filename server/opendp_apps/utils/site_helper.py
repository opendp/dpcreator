"""
Convenience methods for retrieving the current website
"""
from django.contrib.sites.models import Site
from django.conf import settings

def get_current_site_url():
    """Return the current site url, e.g. http://localhost:8000, https://demo.dpcreator.org"""
    current_site = Site.objects.first()
    if not current_site:
        raise ValueError('No current site found!')

    if settings.DPCREATOR_USING_HTTPS:
        site_scheme = 'https://'
    else:
        site_scheme = 'http://'

    site_url = f'{site_scheme}{current_site.domain}'

    if site_url.endswith('/'):
        site_url = site_url[:-1]

    return site_url