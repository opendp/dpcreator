import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from django_cryptography.fields import encrypt

from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.model_helpers.models import TimestampedModelWithUUID


class OpenDPUser(AbstractUser):
    """
    Core App User. May be extended in the future
    """
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    handoff_id = models.UUIDField(\
                    default=uuid.uuid4,
                    null=True,
                    help_text=('Temporary storage of a DataverseHandoff.object_id'
                               ' when arriving from Dataverse.'))

    class Meta:
        verbose_name = 'OpenDP User'

    def __str__(self):
        return self.username #str(self.object_id)


class DataverseUser(TimestampedModelWithUUID):
    """
    Extend the base Django user with
    Dataverse-specific attributes
    """
    user = models.ForeignKey(OpenDPUser,
                             on_delete=models.CASCADE)

    dv_installation = models.ForeignKey(RegisteredDataverse, on_delete=models.PROTECT)

    #TODO: Shouldn't this be unique?
    persistent_id = models.CharField(max_length=255)  # Persistent DV user id within an installation

    email = models.EmailField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    dv_general_token = encrypt(models.CharField(max_length=255, blank=True))

    class Meta:
        verbose_name = 'Dataverse User'
        unique_together = ['user', 'dv_installation']

    def __str__(self):
        return f'{self.user} ({self.dv_installation})'

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure that Dataverse users
        cannot access the Django system via login.
        :param args:
        :param kwargs:
        :return:
        """
        super(DataverseUser, self).save(*args, **kwargs)

    def as_dict(self):
        """
        Return several attributes in dict format
        """
        return dict(id=self.id,
                    user=str(self.user),
                    dv_installation=self.dv_installation,
                    persistent_id=self.persistent_id,
                    email=self.email,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)



class Group(models.Model):
    """
    Organize OpenDP Users into (potentially multiple)
    permission groups, to manage access of releases.
    """
    name = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True, blank=True)


class GroupMembership(models.Model):
    """
    Specify the nature of the User's membership in the group
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class MembershipTypes(models.TextChoices):
        ADMIN = 'AD', 'Admin'
        MEMBER = 'ME', 'Member'
    membership_type = models.CharField(max_length=128, choices=MembershipTypes.choices)


'''
# Move this to a separate app
class DataverseSession(TimestampedModelWithUUID):
    """
    Track user interactions with the system coming from Dataverse.
    """

    # Dataverse user making the request. This will be an extension of the basic
    # Django user object.
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    # This will keep track of overall privacy budget usage via the DepositorInfo FK relationship
    # TODO: Commenting this out due to circular import problem
    # dataset_info = models.ForeignKey(BaseDataSetInfo, null=True, blank=True, on_delete=models.CASCADE)

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
'''
