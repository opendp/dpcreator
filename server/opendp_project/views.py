from django.http import HttpResponse


def home_view(request, *args, **kwargs):
    """
    Useful for testing that server is up
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    return HttpResponse(content="Welcome to OpenDP-UX", status=200)