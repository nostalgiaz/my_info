from django.http import HttpResponse
from django.shortcuts import render
from social.apps.django_app.default.models import UserSocialAuth
from my_info import settings
from twython import Twython
import requests
import simplejson as json


def _get_twitter(request):
    user = UserSocialAuth.objects.filter(provider='twitter').get(
        user=request.user
    )

    return Twython(
        settings.SOCIAL_AUTH_TWITTER_KEY,
        settings.SOCIAL_AUTH_TWITTER_SECRET,
        user.tokens.get('oauth_token'),
        user.tokens.get('oauth_token_secret'),
    )


def _geocoder(location):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address={}' \
          '&sensor=true'.format(location)
    resp = requests.get(url)

    if not resp.json().get('status') == 'ZERO_RESULTS':
        loc = resp.json().get('results')[0].get('geometry').get('location')
        return loc.get('lat'), loc.get('lng')

    return None, None


def _get_map_coords(request):
    data = []

    twitter = _get_twitter(request)

    followers_list = twitter.get_followers_list()

    for user in followers_list.get('users'):
        lat, long = _geocoder(user.get('location'))
        data.append({
            'lat': lat,
            'long': long
        })

    return data


def get_data(request):
    return HttpResponse(
        json.dumps({
            "mapData": _get_map_coords(request),
        }),
        mimetype="application/json"
    )


def home(request):
    return render(request, "main/__site_base.html", )


def my_tweets(request):
    user = UserSocialAuth.objects.filter(provider='twitter').get(
        user=request.user
    )

    twitter = Twython(
        settings.SOCIAL_AUTH_TWITTER_KEY,
        settings.SOCIAL_AUTH_TWITTER_SECRET,
        user.tokens.get('oauth_token'),
        user.tokens.get('oauth_token_secret'),
    )

    my_tweets = twitter.get_user_timeline(**{
        'count': 100
    })

    #f = open('/Users/nostalgia/tweets.json', 'w')
    #f.write(json.dumps(my_tweets))

    name = request.user.first_name
    surname = request.user.last_name

    return render(request, "main/my_tweets.html", {
        'name': name,
        'surname': surname,
        'my_tweets': my_tweets
    })

