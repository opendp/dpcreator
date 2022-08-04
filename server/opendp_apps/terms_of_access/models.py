import os
from urllib import parse

from django.conf import settings
from django.db import models

from opendp_apps.model_helpers.models import TimestampedModelWithUUID


class DifferentTermsOfAccessException(Exception):
    pass


class InvalidTermsOfServiceVersionNumber(Exception):
    pass


class TermsOfAccess(TimestampedModelWithUUID):
    """
    Terms of Access Content
    """
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=True)
    description = models.TextField()
    version = models.FloatField(null=False, blank=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Terms of Access'
        verbose_name_plural = 'Terms of Access'
        ordering = ('active', 'name',)

    def __str__(self):
        return f'{self.name} - v{self.version}'

    def save(self, *args, **kwargs):
        """
        Save a TermsOfAccess model.
        :param args:
        :param kwargs: Potentially contains template_path
        :return:
        """
        # For testing and flexibility, we should allow this method to accept an argument `template_path` which
        # specifies the location of the template to be compared against.
        try:
            template_path = kwargs.pop('template_path')
        except KeyError:
            template_path = os.path.dirname(os.path.realpath(__file__)) + f'/templates/{self.version}.html'
        try:
            with open(template_path, 'r') as infile:
                toa_file = infile.read().replace(' ', '').replace('\n', '').replace('\t', '')
                description = parse.unquote_plus(self.description)
                description = description.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
                if toa_file != description:
                    raise DifferentTermsOfAccessException(f"Invalid description for version {self.version}")
        except FileNotFoundError:
            raise InvalidTermsOfServiceVersionNumber(f"No template file exists for version {self.version}")
        super(TermsOfAccess, self).save(*args, **kwargs)


class TermsOfAccessLog(TimestampedModelWithUUID):
    """
    Records a Terms of Access agreement
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    terms_of_access = models.ForeignKey(TermsOfAccess, on_delete=models.PROTECT)

    verbose_name = 'Terms of Access Log'
    verbose_name_plural = 'Terms of Access Logs'
    ordering = ('-created', 'user')

    def __str__(self):
        return f'{self.user} - {self.terms_of_access}'
