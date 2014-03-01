from __future__ import absolute_import

from my_info.cluster.cache import RedisCache
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify
from my_info.cluster.helpers import get_twitter_from_username
from my_info.cluster.reader import TwitterReader

from my_info.main.celery import app
from my_info.settings import NUMBER_OF_TWEETS


@app.task
def create_info_page_task(username, user_id):
    redis = RedisCache()
    twitter = get_twitter_from_username(username)
    info = twitter.show_user(screen_name=username)

    ###########################################################################
    # PERSONAL INFORMATION
    ###########################################################################

    redis.set("{}:info".format(user_id), {
        'user_id': user_id,
        'full_name': info['name'],
        'nick': info['screen_name'],
        'bio': info['description'],
        'image': info['profile_image_url'].replace('_normal', ''),
        'tweets_count': info['statuses_count'],
        'followers_count': info['followers_count'],
        'following_count': info['friends_count'],
        'location': info['location'],
    })

    ###########################################################################
    # CLUSTER & TWEETS
    ###########################################################################
    k = 20
    if NUMBER_OF_TWEETS < 20:  # debug
        k = 10

    clusterify = SpectralClusterify(TwitterReader(username), k)
    redis.set('{}:step'.format(user_id), 1)

    redis.set("{}:tweets".format(user_id), clusterify.annotate())
    redis.set('{}:step'.format(user_id), 2)

    redis.set("{}:cluster".format(user_id), clusterify.do_cluster())
    redis.set('{}:step'.format(user_id), 3)

    redis.set('{}:step'.format(user_id), 4)  # exit code
