from django.http import HttpResponse


def view_opendp_welcome(request, *args, **kwargs):
    """
    Useful for testing that server is up
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    return HttpResponse(content="Welcome to OpenDP-UX", status=200)