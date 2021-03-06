from __future__ import absolute_import
from celery.utils.log import get_task_logger

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse

from my_info.cluster.cache import RedisCache
from my_info.cluster.clusterify.affinitypropagationclusterify import \
    AffinityPropagationClusterify
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify
from my_info.cluster.clusterify.kmeansclusterify import KMeansClusterify
from my_info.cluster.clusterify.starclusterify import StarClusterify
from my_info.cluster.helpers import get_twitter_from_username
from my_info.cluster.reader import TwitterProfileReader
from my_info.local_settings import EMAIL_HOST_USER

from my_info.main.celery import app
from my_info.main.models import Elaboration, UserInfo
from my_info.settings import NUMBER_OF_TWEETS

logger = get_task_logger(__name__)


@app.task
def create_info_page_task(username, elaboration_id, url):
    elaboration = Elaboration(elaboration_id=elaboration_id)
    redis = RedisCache()
    twitter = get_twitter_from_username(username)
    info = twitter.show_user(screen_name=username)
    user = User.objects.get(username=username)

    ###########################################################################
    # PERSONAL INFORMATION
    ###########################################################################

    try:
        user_info = UserInfo.objects.get(user=user)
    except UserInfo.DoesNotExist:
        user_info = UserInfo()

    user_info.user = user
    user_info.full_name = info['name']
    user_info.nick = info['screen_name']
    user_info.bio = info['description']
    user_info.image = info['profile_image_url'].replace('_normal', '')
    user_info.save()

    ###########################################################################
    # CLUSTER & TWEETS
    ###########################################################################
    k = 50
    if NUMBER_OF_TWEETS <= 20:  # debug
        k = 10

    redis.set('{}:step'.format(elaboration_id), 1)
    # clusterify = KMeansClusterify(TwitterProfileReader(username), k)
    clusterify = AffinityPropagationClusterify(TwitterProfileReader(username), k)
    # clusterify = SpectralClusterify(TwitterProfileReader(username), k)
    # clusterify = StarClusterify(TwitterProfileReader(username))

    redis.set('{}:step'.format(elaboration_id), 2)
    elaboration.tweets = clusterify.annotate()

    redis.set('{}:step'.format(elaboration_id), 3)
    elaboration.cluster = clusterify.do_cluster()

    logger.info(elaboration.cluster)

    redis.set('{}:step'.format(elaboration_id), 4)  # exit code

    elaboration.user = user
    elaboration.save()

    subject, to = "Work done!", user.email

    text_content = "Checkout the final elaboration here: {}".format(url)

    html_content = '<p>Checkout the final elaboration <a href="{}">' \
                   'here</a></p>'.format(url)

    msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()