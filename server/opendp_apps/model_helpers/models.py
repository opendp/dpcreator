"""Abstract Convenience classes"""
import uuid

from django.db import models


class TimestampedModelWithUUID(models.Model):
    """
    Base class for almost all objects in the application
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
