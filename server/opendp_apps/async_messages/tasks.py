from datetime import datetime
from os.path import abspath, dirname, isdir, join

CURRENT_DIR = dirname(abspath(__file__))
SERVER_DIR = dirname(CURRENT_DIR)
TEST_DATA_DIR = join(dirname(SERVER_DIR), 'test_data')

import json
from django.core.serializers.json import DjangoJSONEncoder

from opendp_project.celery import celery_app
from opendp_apps.async_messages.websocket_message import WebsocketMessage

from opendp_apps.profiler.tasks import ProfileHandler
from opendp_apps.profiler import tasks as profiler_tasks

@celery_app.task()#bind=True)
def send_test_msg(websocket_id):


    filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
    #dsi = DataSetInfo.objects.first()

    # with Celery:
    # profiler = ProfileHandler.run_profile_by_filepath.delay(filepath, dsi.object_id)

    profiler = profiler_tasks.run_profile_by_filepath(filepath) #, dsi.object_id)
    if profiler.has_error():
        user_msg = f'error: {profiler.get_err_msg()}'
        print(user_msg)
        ws_msg = WebsocketMessage.get_fail_message( \
            'TYPE_OF_MESSAGE',
            user_msg)
    else:
        profile_str = json.dumps(profiler.data_profile, cls=DjangoJSONEncoder) #, indent=4)
        ws_msg = WebsocketMessage.get_success_message( \
            'TYPE_OF_MESSAGE',
            f'Profile worked {datetime.now()} {profile_str}',
            data=dict(profile=profile_str))
        #print(profiler.data_profile)
        #print()
        #print('profiled!')

    ws_msg.send_message(websocket_id)

    print('celery message sent...')
    return
    # -----------------
    ws_msg = WebsocketMessage.get_success_message( \
        'TYPE_OF_MESSAGE',
        f'Happening via celery {datetime.now()}',
        data=dict(dog=1))

    ws_msg.send_message(websocket_id)

