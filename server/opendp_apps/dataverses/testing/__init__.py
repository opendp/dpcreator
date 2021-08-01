"""
Running individual tests

python manage.py test opendp_apps.dataverses.testing.test_dataverse_handoff_view

python manage.py test opendp_apps.dataverses.testing.test_dv_user_handler
python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePostTest
python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePostTest

docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_downloader_profiler.DownloadProfileTests.test_20_download_errors

docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_downloader_handler.DownloadHandlerTests.test_80_direct_profile




python manage.py test opendp_apps.dataverses.testing.test_file_view.FileViewGetTest.test_10_successful_get

python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePutTest.test_10_successful_creation

python manage.py test opendp_apps.dataverses.testing.test_endpoints.DataversePutTest.test_40_invalid_site_url

python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_030_dv_handler_bad_param
python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_100_check_dv_handler_via_url


docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_downloader_handler.DownloadHandlerTests
#.test_100_check_dv_handler_via_url


docker-compose run server python manage.py test opendp_apps.dataverses.testing.dv_user_handler_test
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_endpoints
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_010_dv_params
docker-compose run server python manage.py test opendp_apps.dataverses.testing.test_dataverse_incoming.DataverseIncomingTest.test_020_check_dv_handler_directly
"""
