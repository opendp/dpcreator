import os

from celery import Celery, shared_task

# set the default Django settings module for the 'celery' program.
from django.conf import settings

celery_app = Celery('dpcreator')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()


#@celery_app.task(bind=True)
#def debug_task(self):
#    print(f'Request: {self.request!r}')

@celery_app.task()#bind=True)
def hello_task():
    from datetime import datetime
    return f'Hello! {datetime.now()}'
