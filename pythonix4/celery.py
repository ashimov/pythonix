from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonix4.settings')

app = Celery('pythonix4')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'celery_on': {
        'task': 'pythonix_admin.tasks.celery_on',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'new_month': {
        'task': 'pythonix_admin.tasks.new_month',
        'schedule': crontab(minute=0, hour=0),
    },
    'clients_off': {
        'task': 'pythonix_admin.tasks.clients_off',
        'schedule': crontab(minute=20, hour=0),
    },
    'deferred_actions_with_customers': {
        'task': 'pythonix_admin.tasks.deferred_actions_with_customers',
        'schedule': crontab(minute='*/5'),
    },
}


