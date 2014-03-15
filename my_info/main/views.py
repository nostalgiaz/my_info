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
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('twitter_callback'))

    return HttpResponseRedirect(reverse('login'))


@login_required()
def twitter_callback(request):
    user = request.user
    if user.email == "":
        return HttpResponseRedirect(reverse('complete_registration'))

    try:
        elaboration_id = Elaboration.objects.filter(
            user__pk=request.user.pk).order_by('-created')[0].elaboration_id

        return HttpResponseRedirect(
            reverse('show_info_page', args=[elaboration_id])
        )

    except IndexError:
        return HttpResponseRedirect(reverse('start_elaboration'))


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
    return HttpResponseRedirect(reverse('twitter_callback'))


def start_elaboration(request):
    user = request.user
    redis = RedisCache()
    elaboration_id = sha1(user.username + str(datetime.now())).hexdigest()

    redis.set('{}:step'.format(elaboration_id), 0)

    create_info_page_task.delay(
        user.username, elaboration_id, request.build_absolute_uri(
            reverse('show_info_page', args=[elaboration_id])
        )
    )

    return HttpResponseRedirect(
        reverse('elaboration', args=[elaboration_id])
    )


def elaboration(request, elaboration_id):
    return render(request, "main/elaboration_process.html", {
        'elaboration_id': elaboration_id
    })


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

