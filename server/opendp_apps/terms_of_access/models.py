from django.db import models
from django.conf import settings
from opendp_apps.datasets.models import BaseDataSetInfo
from opendp_apps.model_helpers.models import \
    (TimestampedModel, TimestampedModelWithUUID)


class TermsOfAccess(TimestampedModel):
    """Terms of Access Content"""
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=True)
    description = models.TextField()
    version = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.name


class TermsOfAccessLog(TimestampedModelWithUUID):
    """Log of Terms of Access"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    terms_of_access = models.ForeignKey(TermsOfAccess, on_delete=models.RESTRICT)
    dataset_info = models.ForeignKey(BaseDataSetInfo, on_delete=models.RESTRICT)

    def __str__(self):
        return f'{self.user} - {self.dataset_info}'
