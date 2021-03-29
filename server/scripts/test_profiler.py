from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import json
from os.path import isfile, join

from django.core.serializers.json import DjangoJSONEncoder
from opendp_apps.profiler.profile_handler import ProfileHandler
from opendp_apps.dataset.models import DataSetInfo


def test_profiler_with_file():
    """Test profiler with file"""
    filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
    dsi = DataSetInfo.objects.first()

    profiler = ProfileHandler.run_profile_by_filepath(filepath, dsi.object_id)
    if profiler.has_error():
        print(f'error: {profiler.get_err_msg()}')
    else:
        print(profiler.data_profile)
        print(json.dumps(profiler.data_profile, cls=DjangoJSONEncoder, indent=4))
        print('profiled!')

    dsi = DataSetInfo.objects.get(object_id=dsi.object_id)
    info = dsi.data_profile_as_dict()
    assert(json.dumps(info, cls=DjangoJSONEncoder) == \
           json.dumps(profiler.data_profile, cls=DjangoJSONEncoder))


def lookat():
    dsi = DataSetInfo.objects.first()
    #print(dsi.data_profile)
    print(type(dsi.data_profile))


    info = dsi.data_profile_as_dict()
    print(info)
    print(info.keys())
    print(type(info))

    jstr = dsi.data_profile_as_json_str()
    print(type(jstr))

if __name__=='__main__':
    test_profiler_with_file()
    # lookat()

