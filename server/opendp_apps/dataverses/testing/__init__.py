"""
Running individual tests

python manage.py test opendp_apps.dataverses.testing.dv_user_handler_test
python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePostTest
python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePutTest


python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_030_dv_handler_bad_param
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_100_check_dv_handler_via_url

docker-compose run server python manage.py test opendp_apps.dataverses.testing.dv_user_handler_test
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_endpoints
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly
"""