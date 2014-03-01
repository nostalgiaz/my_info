from __future__ import absolute_import
import os

from celery import Celery
from my_info import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_info.settings')

app = Celery(
    'main',
    broker=settings.BROKER_URL,
    include=['my_info.main.tasks']
)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


if __name__ == '__main__':
    app.start()