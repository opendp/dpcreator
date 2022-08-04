from celery import Celery

celery_app = Celery('dpcreator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()


@celery_app.task()
def hello_task():
    from datetime import datetime
    return f'Hello! {datetime.now()}'
