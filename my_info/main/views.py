from ajaxutils.decorators import ajax
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from hashlib import sha1

from my_info.cluster.cache import RedisCache

from my_info.cluster.clusterify.kmeansclusterify import KMeansClusterify
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify
from my_info.cluster.clusterify.starclusterify import StarClusterify

from my_info.cluster.helpers import get_twitter_from_username
from my_info.cluster.reader import TwitterReader
from my_info.settings import NUMBER_OF_TWEETS


def home(request):
    pass


@login_required()
def create_info_page(request):
    redis = RedisCache()
    username = request.user.username
    user_id = sha1(username + str(datetime.now())).hexdigest()

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
    redis.set("{}:tweets".format(user_id), clusterify.annotate())
    redis.set("{}:cluster".format(user_id), clusterify.do_cluster())

    return render(request, "main/post_create_info_page.html", {
        'user_id': str(user_id)
    })


def show_info_page(request, user_id):
    redis = RedisCache()
    return render(
        request,
        "main/my_info.html",
        redis.get('{}:info'.format(user_id))
    )


@ajax()
def show_cluster(request, user_id):
    redis = RedisCache()
    return redis.get('{}:cluster'.format(user_id))


@ajax()
def show_tweets(request, user_id):
    redis = RedisCache()
    topics = request.GET.get('topics')
    tweet_list = redis.get('{}:tweets'.format(user_id))
    # remove duplicates
    return [v for k, v in tweet_list.iteritems() if k in topics]
