from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
import requests
import sqlite3
import json
import logging
from sys import stdout
from datetime import datetime
from itertools import chain
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG)

consumer_key="CQ8wPwKADz9FheAOui23uYUjW"
consumer_secret="O0YPIAD5LSmIs5zET8WuBGYviAOcIzhvc2INTbsJaN3YTzy9fA"

access_token="17090112-SWzw6lipXUNMADiIpFhRgvxCBdaV1cqWy3cdMaQIZ"
access_token_secret="LZNdYAmsb3a3XhGHTt5jsVcm5aAtUM6dJUxfTTFpLxuRM"

conn = None

def get_sentiment2(text):
    url = "https://japerk-text-processing.p.mashape.com/sentiment/"

    headers = {
        "X-Mashape-Key": "MU1w0GGHA8mshaHMPY4wNap7sMmip1VvrhWjsnexOzYAM2UqEQ",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    params = {
        "language": "english",
        "text": text
    }


    r = requests.post(url, headers=headers, data=params)
    j = r.json()
    d = j['probability']
    d['label'] = j['label']
    return d



def get_sentiment(text):
    """Using TheySay to analyse a given text"""
    
    headers = { "Content-Type": "application/json" }
    url = "http://apidemo.theysay.io/api/v1/sentiment"
    r = requests.post(url, headers=headers, data=json.dumps({ 'text': text }))
    logging.info('made request, status code = %d' % r.status_code)
    return r.json()['sentiment']


def construct_tweet(candidate, data, sentiment_func=None):
    """Make a dictionary to of the tweet + analysis + candidate"""
    
    row = {
        'id': data['id_str'],
        'tweet': data['text'],
        'posted_by': data['user']['name'],
        'timestamp': datetime.fromtimestamp(int(data['timestamp_ms']) / 1000.0),
        'candidate': candidate,
    }

    if sentiment_func:
        try:
            print(row['tweet'])
            sentiment = sentiment_func(data['text'])
            row.update(sentiment)
            print(sentiment)
        except:
            print("can't get sentiment")
            pass

    return row

def add_row(row, table='tweets4'):
    """Given the json from a tweet and candidate add to the SQLite db
    :params:
    :candidate: this is the string from the keys of the  terms.py dict
    :data: a tweet in JSON
    """
    
    global conn
    
    names = ','.join(row.keys())
    marks = ','.join(['?' for _ in row])
    # table = 'tweets3'
    # table = 'raw_tweets'
    # table = 'logging'



    logging.debug(names)
    logging.debug(list(row.values()))

    qstring = 'INSERT INTO {table} ({names}) VALUES ({marks})'.format(**locals())

    try:
        conn.execute(qstring, list(row.values()))
        logging.info('inserted row into database')
    except sqlite3.IntegrityError as e:
        logging.info('bad values!')
        logging.info(e)

    conn.commit()


class InflatedEgos(StreamListener):

    def __init__(self, *args):
        self._terms = None
        
        
    @property
    def terms(self):
        """Lazy loading of terms from terms.py file"""
        
        if not self._terms:
                logging.info('loading terms')
                termdict = eval(open('terms.py').read())

                tags2name = [[(tag.lower(), name) for tag in tags] for name, tags in termdict.items()]
                self._terms = dict(chain(*tags2name))

        return self._terms


    def on_data(self, jsonstring):
        """This is where all the magic happens"""
        
        data = json.loads(jsonstring)

        # find the candidate in the tweet
        counts = defaultdict(int)
        text = data['text'].lower()
        
        for term, name in self.terms.items():
            if term in text:
                counts[name]+= 1

        # only store if we have 1 candidate
        if len(counts) == 1:
            candidate = list(counts.keys())[0]
            row = construct_tweet(candidate, data)
            add_row(row, "follow1")
            
        else:
            logging.info('Multiple candidates in tweet')

        return True

    def on_error(self, status):
        print(status)

    def on_exception(self, e):
        # import IPython
        # IPython.embed()
        print(e)
        

def analyse_tweets(candidate, handle, filename, table):
    import time

    data = json.loads('[' + open(filename).read()[:-2] + ']')
    
    for d in data:
        if handle in d['text']:
            row = construct_tweet(candidate, d, get_sentiment)
            add_row(row, table)
            time.sleep(0.1)
        

        
if __name__ == '__main__':

    conn = sqlite3.connect('egos.db')

    # analyse_tweets('cameron', '@David_Cameron', '/Users/whg/Desktop/10k_tweets', 'cameron')
    # exit()
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    listener = InflatedEgos()
    stream = Stream(auth, listener)

    follow = {
        "cameron": "103065157",
        "miliband": "61781260",
        "clegg": "15010349",
        "farage": "19017675",
        "sturgeon": "160952087",
        "bennett": "16596200",
        "wood": "14450739",
    }
    
    terms = list(listener.terms.keys())

    follow = list(follow.values())
    print('starting with {0}'.format(terms))
    print('following {0}'.format(follow))
    
    try:
        # stream.filter(track=terms)
        stream.filter(follow=follow)
    except KeyboardInterrupt:
        print('closed connection')

    finally:
        conn.close()
            


    
        
            


    
