from ajaxutils.decorators import ajax

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from my_info.cluster.cache import RedisCache
from my_info.main.tasks import create_info_page_task


def home(request):
    pass


@login_required()
def create_info_page(request):
    from hashlib import sha1
    from datetime import datetime

    redis = RedisCache()
    username = request.user.username
    user_id = sha1(username + str(datetime.now())).hexdigest()

    redis.set('{}:step'.format(user_id), 0)

    create_info_page_task.delay(username, user_id)

    return render(request, "main/post_create_info_page.html", {
        'user_id': user_id
    })


@ajax()
def get_process_status(request, user_id):
    """ step:
        0: get personal information from twitter
        1: get tweets from twitter
        2: annotation using dataTxt
        3: clustering
    """
    redis = RedisCache()
    return {
        'step': redis.get('{}:step'.format(user_id)),
    }


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
    return [v for k, v in tweet_list.iteritems() if k in topics]
