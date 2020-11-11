from django.db import models
from django.db.models import CASCADE


class EmailMessage(models.Model):
    class ContentTypeChoices(models.TextChoices):
        PLAIN_TEXT = 'text/plain'
        HTML = 'application/html'
    content_type = models.CharField(max_length=128, choices=ContentTypeChoices.choices)
    message_template = models.TextField()


class Email(models.Model):
    from_email = models.CharField(max_length=128)
    to_email = models.CharField(max_length=128)
    subject = models.CharField(max_length=128)
    message = models.ForeignKey(EmailMessage, on_delete=CASCADE)
