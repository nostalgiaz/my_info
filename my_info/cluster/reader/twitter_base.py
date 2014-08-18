from my_info.cluster.reader.base import BaseReader
from my_info.settings import NUMBER_OF_TWEETS


class TwitterBaseReader(BaseReader):
    def __init__(self, username, number_of_tweets=NUMBER_OF_TWEETS):
        super(TwitterBaseReader, self).__init__(
            username=username,
            number_of_tweets=number_of_tweets
        )

        self.username = username
        self.number_of_tweets = number_of_tweets
        self.tweet_url = "https://twitter.com/{}/status/{}"

    @staticmethod
    def _get_tweet_text(tweet):
        try:
            return tweet.get("retweeted_status").get("text")
        except:
            return tweet.get('text')

    def create_tweet_object(self, my_wall):
        return [
            (
                self._get_tweet_text(tweet),
                self.tweet_url.format(
                    tweet.get('user').get('screen_name'),
                    tweet.get('id_str')
                ),
                tweet.get('user'),
            ) for tweet in my_wall
        ]

