"""
Running individual tests

python manage.py test opendp_apps.dataverses.testing.dv_user_handler_test
python manage.py test opendp_apps.dataverses.testing.test_endpoints
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly

docker-compose run server python manage.py test opendp_apps.dataverses.testing.dv_user_handler_test
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_endpoints
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly
"""