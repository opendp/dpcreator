from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import json, time
from os.path import isfile, join

from opendp_project.celery import hello_task
from django.core.serializers.json import DjangoJSONEncoder
from opendp_apps.profiler.tasks import ProfileHandler
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler


def test_downloader(dataverse_file_id=3):
    """Test profiler with file"""

    print('get object')
    dfi = DataverseFileInfo.objects.get(pk=dataverse_file_id)
    print('dfi: ', dfi)

    # ---------------------------
    # download check!
    # ---------------------------
    print('-' * 40)
    print('Download Info')
    print('-' * 40)
    dhandler = DataverseDownloadHandler(dfi)
    if dhandler.has_error():
        print('error: ', dhandler.get_err_msg())
        return
    else:
        print('looks good!')

    # ---------------------------
    # profile it!
    # ---------------------------
    print('-' * 40)
    print('Profile it')
    print('-' * 40)
    profile_handler = profiler_tasks.run_profile_by_filefield(dfi.object_id)
    if profile_handler.has_error():
        print('error: ', profile_handler.get_err_msg())
        return
    else:
        print(profile_handler.data_profile)
        print(json.dumps(profile_handler.data_profile, cls=DjangoJSONEncoder, indent=4))
        print('profiled!')



if __name__=='__main__':
    test_downloader(dataverse_file_id=5)

"""
docker-compose run server python scripts_dev/test_downloader.py
docker-compose run server python scripts_dev/test_profiler.py

docker-compose run server python manage.py dumpdata dataverses.registereddataverse --indent=4 --pks=1
docker-compose run server python manage.py dumpdata dataset.datasetinfo --indent=4 --pks=3
docker-compose run server python manage.py dumpdata analysis.depositorsetupinfo --indent=4 --pks=3

docker-compose run server python manage.py dumpdata dataset.dataversefileinfo  --indent=4 --pks=3

"""