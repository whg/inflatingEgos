from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
import requests
import sqlite3
import json
import logging
from datetime import datetime
from itertools import chain
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

consumer_key="CQ8wPwKADz9FheAOui23uYUjW"
consumer_secret="O0YPIAD5LSmIs5zET8WuBGYviAOcIzhvc2INTbsJaN3YTzy9fA"

access_token="17090112-SWzw6lipXUNMADiIpFhRgvxCBdaV1cqWy3cdMaQIZ"
access_token_secret="LZNdYAmsb3a3XhGHTt5jsVcm5aAtUM6dJUxfTTFpLxuRM"

conn = None

def get_sentiment(text):
    headers = { "Content-Type": "application/json" }
    url = "http://apidemo.theysay.io/api/v1/sentiment"
    r = requests.post(url, headers=headers, data=json.dumps({ 'text': text }))
    logging.info('made request, status code = %d' % r.status_code)
    return r.json()['sentiment']


def add_row(candidate, data):

    global conn
    
    row = {
        'id': data['id'],
        'tweet': data['text'],
        'posted_by': data['user']['name'],
        'timestamp': datetime.fromtimestamp(int(data['timestamp_ms']) / 1000.0),
        'candidate': candidate,
    }

    sentiment = get_sentiment(data['text'])
    row.update(sentiment)
    
    names = ','.join(row.keys())
    marks = ','.join(['?' for _ in row])
    table = 'tweets3'

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
        if not self._terms:
                logging.info('loading terms')
                termdict = eval(open('terms.py').read())

                tags2name = [[(tag.lower(), name) for tag in tags] for name, tags in termdict.items()]
                self._terms = dict(chain(*tags2name))

        return self._terms


    #StreamListener func
    
    def on_data(self, jsonstring):

        data = json.loads(jsonstring)

        counts = defaultdict(int)

        text = data['text'].lower()
        for term, name in self.terms.items():
            if term in text:
                counts[name]+= 1

        # only store if we have 1 candidate

        if len(counts) == 1:
            add_row(list(counts.keys())[0], data)
        else:
            logging.info('Multiple candidates in tweet')

        return True

    def on_error(self, status):
        print(status)

    def on_exception(self, e):
        # import IPython
        # IPython.embed()
        print(e)
        

if __name__ == '__main__':

    conn = sqlite3.connect('egos.db')
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    listener = InflatedEgos()
    stream = Stream(auth, listener)

    terms = list(listener.terms.keys())
    print('starting with {0}'.format(terms))
    
    try:
        stream.filter(track=terms)
    except KeyboardInterrupt:
        conn.close()
        print('closed connection')


    
        
            


    
