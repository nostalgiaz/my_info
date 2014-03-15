from hashlib import sha1
from datetime import datetime

from ajaxutils.decorators import ajax

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404

from my_info.cluster.cache import RedisCache
from my_info.main.models import Elaboration, UserInfo
from my_info.main.tasks import create_info_page_task


def home(request):
    return HttpResponseRedirect(reverse('login'))


@login_required()
def save_email(request, user_pk):
    import re

    email_request = request.POST.get("email")
    email = re.match(
        r'[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}', email_request
    )

    if not email:
        return render(request, "main/complete_registration.html", {
            'user_id': user_pk,
            'email': email_request,
            'error': 'email is required'
        })

    user = User.objects.get(pk=user_pk)
    user.email = email.group()
    user.save()
    return HttpResponseRedirect(reverse('create_info_page'))


@login_required()
def create_info_page(request):
    if request.user.email != "":
        redis = RedisCache()
        username = request.user.username
        user_id = sha1(username + str(datetime.now())).hexdigest()

        redis.set('{}:step'.format(user_id), 0)
        create_info_page_task.delay(
            username, user_id, request.build_absolute_uri(
                reverse('show_info_page', args=[user_id])
            )
        )

        return render(request, "main/elaboration_process.html", {
            'user_id': user_id
        })

    return HttpResponseRedirect(reverse('complete_registration'))


def elaboration_history(request, user_pk):
    elaborations = get_list_or_404(
        Elaboration.objects.order_by('-created'), user__pk=user_pk)

    user_info = UserInfo.objects.get(user__pk=user_pk)

    return render(request, "main/elaboration_history.html", {
        'elaborations': elaborations,
        'image': user_info.image,
        'full_name': user_info.full_name,
        'bio': user_info.bio,
        'nick': user_info.nick,
    })


def show_info_page(request, user_id):
    elaboration = get_object_or_404(Elaboration, elaboration_id=user_id)
    user_info = UserInfo.objects.get(user=elaboration.user)

    redis = RedisCache()
    redis.delete('{}:step'.format(user_id))

    return render(request, "main/elaboration_render.html", {
        'user_id': user_id,
        'image': user_info.image,
        'full_name': user_info.full_name,
        'bio': user_info.bio,
        'nick': user_info.nick,
    })


@ajax()
def get_process_status(request, user_id):
    redis = RedisCache()
    return {
        'step': redis.get('{}:step'.format(user_id)),
    }


@ajax()
def show_cluster(request, user_id):
    elaboration = Elaboration.objects.get(elaboration_id=user_id)
    return elaboration.cluster


@ajax()
def show_tweets(request, user_id):
    elaboration = Elaboration.objects.get(elaboration_id=user_id)
    topics = request.GET.get('topics')

    tweet_list = []
    tweet_set = set()

    for k, v in elaboration.tweets.iteritems():
        text = v[0]['text']
        if k in topics and text not in tweet_set:
            tweet_set.add(text)
            tweet_list.append(v)

    return tweet_list

