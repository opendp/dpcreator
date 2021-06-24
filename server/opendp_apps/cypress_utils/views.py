from django.shortcuts import Http404
from django.core.management import call_command
from django.http import JsonResponse
from opendp_apps.cypress_utils.check_setup import are_cypress_settings_in_place


def clear_test_data(request):
    """
    Should only be available during cypress tests
    """

    # Note: this check is made again in the command
    #
    if not are_cypress_settings_in_place():
        raise Http404('nothing here')

    call_command('clear_test_data')
    return JsonResponse({'success': True,
                         'message': 'Data cleared'})