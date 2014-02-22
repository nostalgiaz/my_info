from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth

from twython import Twython
from my_info import settings


def _get_twitter_handler(token, secret):
    return Twython(
        settings.SOCIAL_AUTH_TWITTER_KEY,
        settings.SOCIAL_AUTH_TWITTER_SECRET,
        token,
        secret,
    )


def get_twitter_from_username(username):
    user = UserSocialAuth.objects.filter(provider='twitter').get(
        user=User.objects.get(username=username)
    )

    return _get_twitter_handler(
        user.tokens.get('oauth_token'),
        user.tokens.get('oauth_token_secret')
    )