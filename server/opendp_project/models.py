import uuid as uuid

from django.contrib.auth.models import User
from django.db import models


class DataverseFile(models.Model):
    """
    Placeholder so we can have a foreign key
    in the Session object.
    """

    # TODO: Many2Many relationship with DPRequests

    # Defines the privacy budget, set by depositor
    epsilon = models.FloatField(null=False, blank=False)


class DataverseUser(User):
    """
    Extend the base Django user with
    Dataverse-specific attributes
    """

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure that Dataverse users
        cannot access the Django system via login.
        :param args:
        :param kwargs:
        :return:
        """
        self.set_unusable_password()
        super(DataverseUser, self).save(*args, **kwargs)


class Session(models.Model):
    """
    Track user interactions with the system coming from Dataverse.
    """

    # Unique id used for external representations (URLs, display, etc.) so as not
    # to expose internal ids
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4, editable=False)

    # Dataverse user making the request. This will be an extension of the basic
    # Django user object.
    user = models.ForeignKey(DataverseUser,
                             on_delete=models.CASCADE)

    # This will keep track of overall privacy budget usage.
    dataverse_file = models.ForeignKey(DataverseFile, null=True, blank=True, on_delete=models.CASCADE)

    class SessionTypes(models.TextChoices):
        DEPOSITOR = 'DE', 'Depositor'
        ANALYST = 'AN', 'Analyst'

    session_type = models.CharField(max_length=2, choices=SessionTypes.choices)

    # The status will be updated as each step is completed.
    class Statuses(models.IntegerChoices):
        PREPARATION = 1, 'Preparation'
        STAT_CREATION = 2, 'Statistic Creation'
        AWAITING_EXECUTION_ENGINE = 3, 'Awaiting Execution Engine'
        ERROR = 4, 'Error'
        DEPOSIT_COMPLETE = 5, 'Dataverse Deposit Complete'

    status = models.IntegerField(default=Statuses.PREPARATION, choices=Statuses.choices)

    # TODO: This may go somewhere else
    terms_of_use_accepted = models.BooleanField(default=False)

    # TODO: This may become its own table
    request_parameters = models.JSONField()

    # Key for Redis cache, which stores parameters for X number of hours
    # before ejecting. Redis keys can be basically arbitrarily large, so
    # leaving this as a TextField for now.
    token_parameters_key = models.TextField()
