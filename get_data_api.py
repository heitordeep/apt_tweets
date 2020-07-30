import json
from datetime import datetime

import tweepy
from azure.storage.blob import BlobClient, BlobServiceClient
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
        self.date_now = f'{self.now.year}{self.now.month}{self.now.day}{self.now.hour}{minute}'
        self.blob = BlobServiceClient.from_connection_string(
            config('connect_string')
        )
        self.partition = []

    def get_data(self, find_tweet):
        items = []

        minute = lambda minute: '00' if minute <= '29' else '30'
        for tweet in tweepy.Cursor(
            self.api.search,
            q=find_tweet,
            until=datetime.today().strftime('%Y-%m-%d'),
        ).items():
            if find_tweet in tweet.text:
                data = tweet.created_at
                now = f'{data.year}{str(data.month).zfill(2)}{str(data.day).zfill(2)}{str(data.hour).zfill(2)}{minute(str(data.minute))}'
                items.append({'created_at': now, 'text': tweet.text})
                if now not in self.partition:
                    self.partition.append(now)

        return items

    def blob_input(self, tweets, date, verification):
        for tweet in tweets:
            self.connect_container = self.blob.get_blob_client(
                    container=config('container'),
                    blob=f'RawData/tweets_{tweet["created_at"]}.json'
                    # blob=f'RawData/{tweet["created_at"]}/tweets_{tweet["created_at"]}.json',
            )
            
            if verification:                    
                try:       
                    self.connect_container.upload_blob(
                        json.dumps(tweet, ensure_ascii=False, overwrite=True)
                    )
                except:
                    pass
            else:

                try:
                    self.connect_container.upload_blob(
                        json.dumps(tweet, ensure_ascii=False)
                    )
                except:
                    pass
        


    def check_blob(self, tweets):
        verification = False

        try:
            container_client = self.blob.get_container_client(config('container'))
            container_list = container_client.list_blobs()
            file_list = container_client.list_blobs()
            
            path_blob = [f'RawData/{date}/tweets_{date}' for date in self.partition]

            for blob in file_list:                
                if blob.name in path_blob:
                    verification = True
                self.blob_input(tweets, self.partition, verification)

        except StopIteration:
            pass
        finally:
            self.blob_input(tweets, self.partition, verification)
            


minute = '30'
if datetime.now().minute <= 29:
    minute = '00'

get_tweets = TweetFinder(minute=minute)
tweets = get_tweets.get_data(find_tweet='Caieiras')
get_tweets.check_blob(tweets)