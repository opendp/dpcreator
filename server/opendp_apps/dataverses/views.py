from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse

from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.dataverses.models import ManifestTestParams


# Limit this to superusers!!!
@user_passes_test(lambda u: u.is_superuser)
def view_as_dict(request, object_id):
    """Return the ManifestTestParams in JSON format"""
    mparams = ManifestTestParams.objects.filter(object_id=object_id).first()
    if not mparams:
        return JsonResponse(get_json_error('Object not found'), status=HTTPStatus.NOT_FOUND)

    return JsonResponse(get_json_success('Success', data=mparams.as_dict()))


