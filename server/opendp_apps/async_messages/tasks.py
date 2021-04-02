from datetime import datetime

from opendp_project.celery import celery_app
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.async_messages.consumers import ChatConsumer


@celery_app.task()#bind=True)
def hello_task(websocket_id):


    return f'Hello! {datetime.now()}'
