from django.urls import path
from opendp_apps.cypress_utils import views

urlpatterns = [

    path(f'clear-test-data',
            views.clear_test_data,
            name='clear_test_data'),
]