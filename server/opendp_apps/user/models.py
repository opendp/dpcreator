import uuid as uuid
from django.contrib.auth.models import User
from django.db import models

from ..dataverse.models import DataverseFile


class DataverseUser(User):
    """
    Extend the base Django user with
    Dataverse-specific attributes
    """

    # Which dataverse installation user is on
    installation = models.CharField(max_length=128, null=False, blank=False)

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure that Dataverse users
        cannot access the Django system via login.
        :param args:
        :param kwargs:
        :return:
        """
        self.set_unusable_password()
        # Some combination of Dataverse user id + installation name
        # since we can't guarantee uniqueness across installations
        self.username = '-'.join([self.email, self.installation])
        if not self.email or not self.installation:
            raise Exception('Email and installation must be defined')
        super(DataverseUser, self).save(*args, **kwargs)


class Group(models.Model):
    """
    Organize DataverseUsers into (potentially multiple)
    permission groups, to manage access of releases.
    """
    name = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True, blank=True)


class GroupMembership(models.Model):
    """
    Specify the nature of the User's membership in the group
    """
    user = models.ForeignKey(DataverseUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class MembershipTypes(models.TextChoices):
        ADMIN = 'AD', 'Admin'
        MEMBER = 'ME', 'Member'
    membership_type = models.CharField(max_length=128, choices=MembershipTypes.choices)


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

    # TODO: Should this be moved out of this class to be reused in "analysis"?
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
