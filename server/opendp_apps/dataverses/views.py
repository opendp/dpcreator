from http import HTTPStatus
import uuid

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse

from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.dataverses.models import DataverseHandoff, ManifestTestParams
from opendp_apps.dataverses.forms import DataverseHandoffForm


@login_required
def view_dataverse_handoff(request):
    """Temporarily save the Dataverse paramemeters +
    redirect to the Vue page"""
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = DataverseHandoffForm(request.GET)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_obj = form.save()
            # would redirect to Vue page here!!!

            client_url = reverse('vue-home') + f'?id={str(new_obj.object_id)}'
            print('client_url', client_url)
            return HttpResponseRedirect(client_url)

            return JsonResponse(dict(message='ok',
                                     uuid=str(new_obj.object_id)))

        # if a GET (or any other method) we'll create a blank form
        else:
            return JsonResponse(dict(message='Form errors!',
                                data=form.errors))#.as_json()))

    return JsonResponse(dict(message='No GET data!!!!'))


# make superuser only
@login_required
def view_handoff_params_test(request, object_id=None):
    """
    Create a Dataverse user via a POST request
    - OpenDPUser id
    - DataverseHandoff object id
    """
    if not settings.DEBUG:
        raise Http404('Only for testing')

    # ---------------------------------------
    # Change the object_id to a proper UUID
    # ---------------------------------------
    object_as_uuid = None
    try:
        object_as_uuid = uuid.UUID(object_id)
    except ValueError as err_obj:
        message = 'Bad UUID!'
        return JsonResponse(dict(message=message),
                            status=HTTPStatus.BAD_REQUEST)

    # ---------------------------------------
    # Retrieve the DataverseHandoff object
    # ---------------------------------------
    try:
        handoff_params = DataverseHandoff.objects.get(object_id=object_as_uuid)
        message = f'Found params!! {handoff_params}'
    except DataverseHandoff.DoesNotExist:
        message = 'No handoff params found!!'

    info = dict(message=message,
                object_id=object_id)

    return JsonResponse(info)


"""
http://127.0.0.1:8000/api/dataverses/handoff?fileId=4034504&siteUrl=https%3A%2F%2Fdataverse.harvard.edu%2F&apiSensitiveDataReadToken=some-token&apiGeneralToken=some-other-token&datasetPid=doi%3A10.7910%2FDVN%2FB7DHBK&filePid=doi%3A10.7910%2FDVN%2FB7DHBK%2FBSNYLQ

http://127.0.0.1:8000/api/dataverses/view-handoff-params
"""


# Limit this to superusers!!!
@user_passes_test(lambda u: u.is_superuser)
def view_as_dict(request, object_id):
    """Return the ManifestTestParams in JSON format"""
    mparams = ManifestTestParams.objects.filter(object_id=object_id).first()
    if not mparams:
        return JsonResponse(get_json_error('Object not found'), status=HTTPStatus.NOT_FOUND)

    return JsonResponse(get_json_success('Success', data=mparams.as_dict()))
