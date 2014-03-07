from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField


class Elaboration(TimeStampedModel):
    elaboration_id = models.CharField(max_length=40)
    user = models.ForeignKey(User)
    info = JSONField()
    tweets = JSONField()
    cluster = JSONField()
