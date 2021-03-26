from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import json
from os.path import isfile, join

from opendp_apps.profiler.profile_handler import ProfileHandler


def test_profiler():
    print('hi')

    filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
    profiler = ProfileHandler.run_profile_by_filepath(filepath)
    if profiler.has_error():
        print(f'error: {profiler.get_err_msg()}')
    else:
        print(profiler.data_profile)
        print(json.dumps(profiler.data_profile))
        print('profiled!')

if __name__=='__main__':
    test_profiler()

