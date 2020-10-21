from django.db import models
from django.contrib.auth.models import AbstractUser
from opendp_apps.model_helpers.models import \
    (TimestampedModel, TimestampedModelWithUUID)


class User(AbstractUser, TimestampedModel):
    # add additional fields as needed
    pass

