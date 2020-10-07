from django.db import models


class DataverseFile(models.Model):
    """
    Placeholder so we can have a foreign key
    in the Session object.
    """

    # TODO: Many2Many relationship with DPRequests

    # Defines the privacy budget, set by depositor
    epsilon = models.FloatField(null=False, blank=False)