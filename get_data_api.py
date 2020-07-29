import json
from datetime import datetime

import tweepy
from azure.storage.blob import BlobClient
from decouple import config

class TweetFinder:
    def __init__(self, minute):
        self.auth = tweepy.OAuthHandler(
            config('consumer_key'), config('consumer_secret')
        )
        self.auth.set_access_token(
            config('access_token'), config('access_secret')
        )
        self.api = tweepy.API(self.auth)
        self.now = datetime.now()
        self.date_now = f'{self.now.year}{self.now.month}{self.now.day}{self.now.hour}{minute}{self.now.second}'
        self.date_now_folder = f'{self.now.year}{self.now.month}{self.now.day}{self.now.hour}{minute}'
        self.blob = BlobClient(
            account_url=config('account_url'),
            container_name=config('container'),
            blob_name=f'RawData_{self.date_now_folder}/tweets_{self.date_now}.json',
            credential=config('credential'),
        )

    def get_data(self, find_tweet):
        items = []
        
        for tweet in tweepy.Cursor(
            self.api.search,
            q=find_tweet,
            until=datetime.today().strftime('%Y-%m-%d'),
        ).items():
            if find_tweet in tweet.text:
                items.append({'Date': str(tweet.created_at), 'Text': tweet.text})

        return items        

    def input_blob(self, tweets):

        self.blob.upload_blob(json.dumps(tweets, ensure_ascii=False))

        print('Upload Success...')


# -----------------------------------

minute = '30'
if datetime.now().minute <= 29:
   minute = '00'

get_tweets = TweetFinder(minute=minute)
tweets = get_tweets.get_data(find_tweet='Caieiras')
get_tweets.input_blob(tweets)
