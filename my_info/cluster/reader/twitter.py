"""
TwitterReader
"""
from django.conf import settings
from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth
from twython import Twython
from my_info.cluster.reader.base import BaseReader


class TwitterReader(BaseReader):
    def __init__(self, username, number_of_tweets=10):
        super(TwitterReader, self).__init__(
            username=username,
            number_of_tweets=number_of_tweets
        )

        self.username = username
        self.number_of_tweets = number_of_tweets

    def _texts(self):
        user = UserSocialAuth.objects.filter(provider='twitter').get(
            user=User.objects.get(username=self.username)
        )

        twitter = Twython(
            settings.SOCIAL_AUTH_TWITTER_KEY,
            settings.SOCIAL_AUTH_TWITTER_SECRET,
            user.tokens.get('oauth_token'),
            user.tokens.get('oauth_token_secret'),
        )

        my_tweets = twitter.get_user_timeline(**{
            'count': self.number_of_tweets
        })

        return [tweet.get('text') for tweet in my_tweets]
