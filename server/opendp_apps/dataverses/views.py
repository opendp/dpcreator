from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.forms import DataverseHandoffForm



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

"""
http://127.0.0.1:8000/api/dataverses/handoff?fileId=4034504&siteUrl=https%3A%2F%2Fdataverse.harvard.edu%2F&apiSensitiveDataReadToken=some-token&apiGeneralToken=some-other-token&datasetPid=doi%3A10.7910%2FDVN%2FB7DHBK&filePid=doi%3A10.7910%2FDVN%2FB7DHBK%2FBSNYLQ
"""


# Limit this to superusers!!!
@user_passes_test(lambda u: u.is_superuser)
def view_as_dict(request, object_id):
    """Return the ManifestTestParams in JSON format"""
    mparams = ManifestTestParams.objects.filter(object_id=object_id).first()
    if not mparams:
        return JsonResponse(get_json_error('Object not found'), status=HTTPStatus.NOT_FOUND)

    return JsonResponse(get_json_success('Success', data=mparams.as_dict()))
