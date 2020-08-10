import json
from datetime import datetime as dt
from datetime import timedelta
from re import IGNORECASE, compile

from azure.storage.blob import BlobServiceClient
from decouple import config
from tweepy import API, Cursor, OAuthHandler
from tweepy.error import TweepError


class TweetFinder:
    def __init__(self):
        self.auth = OAuthHandler(
            config('consumer_key'), config('consumer_secret')
        )
        self.auth.set_access_token(
            config('access_token'), config('access_secret')
        )
        self.api = API(self.auth)
        self.blob = BlobServiceClient.from_connection_string(
            config('connect_string')
        )
        self.container_client = self.blob.get_container_client(
            config('container')
        )
        self.now = dt.now()
        self.payload = []
        self.tweets = []

    def get_data(self, find_tweet):
        rgx_tweet = compile(f'.*({find_tweet}).*', IGNORECASE)

        today = dt.today().strftime('%Y-%m-%d')
        tweets = Cursor(self.api.search, q=find_tweet, since=today).items()

        try:
            for tweet in tweets:
                if rgx_tweet.match(tweet.text):
                    self.payload.append({
                            'created_at': str(
                                tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            ),
                            'text': tweet.text,
                        }
                    )
        except TweepError as e:
            print(f'Erro: {e}')

    def insert_in_blob(self):

        verification_date = self.verification_date()

        for tweet in self.payload:

            if tweet['created_at'] >= str(
                verification_date['start']
            ) and tweet['created_at'] <= str(verification_date['final']):
                self.tweets.append(tweet)

        self.upload_file(verification_date['start'])

    def upload_file(self, dt_partition):

        partition = (dt_partition + timedelta(hours=1)) - timedelta(minutes=30)

        self.connect_container = self.blob.get_blob_client(
            container=config('container'),
            blob=(
                f'RawData/{partition.strftime(f"%Y%m%d")}'
                f'/{partition.strftime(f"%H")}'
                f'/{partition.strftime(f"%M")}'
                f'/tweets_{partition.strftime(f"%Y%m%d%H%M")}.json'
            ),
        )
        self.connect_container.upload_blob(
            json.dumps(self.tweets, ensure_ascii=False)
        )

    def verification_date(self):

        if self.now.minute <= 29:
            start_datetime = self.now.replace(
                microsecond=0, second=0, minute=30
            ) - timedelta(hours=1)
            final_datetime = self.now.replace(
                microsecond=0, second=59, minute=59
            ) - timedelta(hours=1)
        else:
            start_datetime = self.now.replace(
                microsecond=0, second=0, minute=0
            )
            final_datetime = self.now.replace(
                microsecond=0, second=59, minute=29
            )

        return {'start': start_datetime, 'final': final_datetime}


if __name__ == '__main__':
    text = 'Caieiras'
    get_tweets = TweetFinder()
    get_tweets.get_data(find_tweet=text)
    get_tweets.insert_in_blob()
