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
        self.container_client = self.blob.get_container_client(config('container'))
        self.partitions = {}

    def get_data(self, find_tweet, retroactive):
        rgx_tweet = compile(f'.*({find_tweet}).*', IGNORECASE)

        if retroactive:
            tweets = Cursor(self.api.search, q=find_tweet).items()
        else:
            yesterday = (dt.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            tweets = Cursor(
                self.api.search, q=find_tweet, since=yesterday
            ).items()

        try:
            for tweet in tweets:
                if rgx_tweet.match(tweet.text):
                    self._store_tweet(tweet)
        except TweepError as e:
            print(e)

    def _store_tweet(self, tweet):
        tweet_date = tweet.created_at
        # minute = lambda minute: '00' if minute <= 29 else '30'
        # date = tweet_date.strftime(f"%Y%m%d%H{minute(tweet_date.minute)}")
        date = tweet_date.strftime("%Y%m%d")
        payload = {
            'id': tweet.id,
            'created_at': tweet_date.strftime(f"%Y-%m-%d %H:%M"),
            'text': tweet.text,
        }

        if date not in self.partitions:
            self.partitions[date] = [payload]
        else:
            self.partitions[date].append(payload)

    def check_blob(self):

            file_list = self.container_client.list_blobs(
                name_starts_with='RawData/'
            )
            
            path_blob = {
                f'RawData/tweets_{key}.json' for key in self.partitions.keys()
            } 

            for blob in file_list:
                if blob.name not in path_blob:  
                    import ipdb; ipdb.set_trace()
                    
                    for partition, tweets in self.partitions.items(): 

                        self.connect_container = self.blob.get_blob_client(
                            container=config('container'),
                            blob=f'RawData/tweets_{partition}.json'
                        )
                        self.connect_container.upload_blob(
                            json.dumps(tweets, ensure_ascii=False)
                        )
            
if __name__ == '__main__':
    text = 'Caieiras'
    retroactive = True
    get_tweets = TweetFinder()
    get_tweets.get_data(find_tweet=text, retroactive=retroactive)
    get_tweets.check_blob()
