from __future__ import absolute_import

from celery import Celery
from my_info.settings import BROKER_URL, CELERY_RESULT_BACKEND

app = Celery(
    'main',
    broker=BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['my_info.main.tasks']
)

if __name__ == '__main__':
    app.start()