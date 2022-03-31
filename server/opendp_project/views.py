import logging

from django.http import HttpResponse
from rest_framework import permissions, viewsets


def home_view(request, *args, **kwargs):
    """
    Useful for testing that server is up
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    return HttpResponse(content="Welcome to OpenDP-UX", status=200)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    We want all lookups to happen via the object_id.
    Inheriting from this class guarantees that a "detail view"
    (e.g. /api/dataset-info/<id>/ expects that <id> is actually
    object_id rather than the primary key in the database
    """
    lookup_field = 'object_id'
    permission_classes = [permissions.IsAuthenticated]
    logger = logging.getLogger('azure')
    event_logger = logging.getLogger()
