from django.shortcuts import render
from social.apps.django_app.default.models import UserSocialAuth
from my_info import settings
from twython import Twython


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
        'count': 10
    })

    name = request.user.first_name
    surname = request.user.last_name

    return render(request, "main/my_tweets.html", {
        'name': name,
        'surname': surname,
        'my_tweets': my_tweets
    })