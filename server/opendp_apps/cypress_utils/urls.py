from django.urls import path
from opendp_apps.cypress_utils import views

urlpatterns = [
    # /cypress-tests/clear-test-data/
    path(f'clear-test-data/',
         views.clear_test_data,
         name='clear_test_data'),
    #
    # /cypress-tests/clear-test-data/
    path(f'clear-test-datasets/',
         views.clear_test_datasets,
         name='clear_test_datasets'),
    #
    # /cypress-tests/setup-demo-data/
    path(f'setup-demo-data/',
         views.setup_demo_data,
         name='setup_demo_data'),
]
