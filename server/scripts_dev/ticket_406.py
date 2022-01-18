from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import json, time
from os.path import isfile, join

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.dataset.models import *


def examine_release():
    """Test profiler with file"""
    ri = ReleaseInfo.objects.first()
    if ri is None:
        print('ReleaseInfo not found!')
        return

    print('\n-- release --')
    print('dp_release_json_file', ri.dp_release_json_file)
    print('dp_release_json_file.path', ri.dp_release_json_file.path)
    print('dp_release_json_file.name', ri.dp_release_json_file.name)
    print('dp_release_json_file.url', ri.dp_release_json_file.url)


    fh = ri.dp_release_json_file.open()

    print('dp_release_json_file.open()', fh.read()[:400])

    print('\n-- dataset --')
    print('source_file.path', ri.dataset.source_file.path)
    print('source_file.url', ri.dataset.source_file.url)

def ticket_414():
    import os
    from pprint import pprint
    from django.conf import settings
    from opendp_apps.profiler.csv_reader import CsvReader
    from opendp_apps.profiler.variable_info import VariableInfoHandler

    fname = 'Fatigue_data.tab'
    # fname = 'teacher_climate_survey_lwd.csv'
    csv_reader = CsvReader(os.path.join(settings.BASE_DIR, 'test_data', fname))
    df = csv_reader.read()
    v = VariableInfoHandler(df)
    profile_dict = v.run_profile_process()
    import json
    print(json.dumps(profile_dict, indent=4))


if __name__=='__main__':
    # examine_release()
    ticket_414()

"""
docker-compose run server python scripts_dev/test_profiler.py
"""