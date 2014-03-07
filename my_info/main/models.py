from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField


class UserInfo(models.Model):
    user = models.OneToOneField(User)
    nick = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255)
    bio = models.TextField()


class Elaboration(TimeStampedModel):
    elaboration_id = models.CharField(max_length=40)
    user = models.ForeignKey(User)
    tweets = JSONField()
    cluster = JSONField()
