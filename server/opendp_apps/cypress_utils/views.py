from django.shortcuts import Http404
from django.core.management import call_command
from django.http import JsonResponse
from opendp_apps.cypress_utils.check_setup import are_cypress_settings_in_place


def clear_test_data(request):
    """
    Should only be available during cypress tests
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False,
                             'message': 'nothing 1'},
                            status=404)

    if not request.user.is_superuser:
        return JsonResponse({'success': False,
                             'message': 'nothing 2'},
                            status=404)

    # Note: this check is made again in the command
    #
    if not are_cypress_settings_in_place():
        return JsonResponse({'success': False,
                             'message': 'nothing 3'},
                            status=404)

    call_command('clear_test_data')

    return JsonResponse({'success': True,
                         'message': 'Data cleared'})