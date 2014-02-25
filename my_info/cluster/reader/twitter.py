"""
TwitterReader
"""
from my_info.cluster.helpers import get_twitter_from_username
from my_info.cluster.reader.base import BaseReader
from my_info.settings import NUMBER_OF_TWEETS


class TwitterReader(BaseReader):
    def __init__(self, username, number_of_tweets=NUMBER_OF_TWEETS):
        super(TwitterReader, self).__init__(
            username=username,
            number_of_tweets=number_of_tweets
        )

        self.username = username
        self.number_of_tweets = number_of_tweets

    def _texts(self):
        url = "https://twitter.com/{}/status/{}"

        twitter = get_twitter_from_username(self.username)

        my_wall = twitter.get_home_timeline(**{
            'count': self.number_of_tweets
        })

        return [(
            tweet.get('text'),
            url.format(tweet.get('user').get('screen_name'),
                       tweet.get('id_str')),
            tweet.get('user'),
        ) for tweet in my_wall]
