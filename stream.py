from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
import requests
import sqlite3
import json
import logging
import threading
import time
from datetime import datetime
from itertools import chain
from collections import defaultdict

from twitter_infos import infos
from osc_helpers import *

logging.basicConfig(level=logging.DEBUG)


consumer_key="CQ8wPwKADz9FheAOui23uYUjW"
consumer_secret="O0YPIAD5LSmIs5zET8WuBGYviAOcIzhvc2INTbsJaN3YTzy9fA"

access_token="17090112-SWzw6lipXUNMADiIpFhRgvxCBdaV1cqWy3cdMaQIZ"
access_token_secret="LZNdYAmsb3a3XhGHTt5jsVcm5aAtUM6dJUxfTTFpLxuRM"


from sentiment import get_sentiment, get_sentiment2
from saving import *
from scrape import poll_candidates

osc_client = None

class InflatedEgos(StreamListener):

    def __init__(self, *args):
        self._terms = None
        self.clients = {}
        
        
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

        add_row_mongo(data)

        # global osc_client
        # if not osc_client:
        #     # osc_client = udp_client.UDPClient('192.168.0.83', 5005)
        #     osc_client = udp_client.UDPClient('localhost', 5005)
            

        import re
        for v in infos.values():
            r = '|'.join(v['tags'])
            
            if re.search(r, data['text'], re.IGNORECASE):
                candidate = v['short_name']
                # if 'client' not in infos[candidate]:
                #     if not 'ip' in v:
                #         print('no ip for %s' % (candidate))
                #         break

                #     # v['ip'] = "localhost"
                #     infos[candidate]['client'] = udp_client.UDPClient(v['ip'], v['osc_po
                    # rt'])
                    
                mess = tweet_message(data)

                send_message(candidate, mess)
                
                # print('sending %s to %s on port %s on %s' % (mess, candidate, v['osc_port'], v['ip']))
                # try:
                #     infos[candidate]['client'].send(mess)
                # except RuntimeError:
                #     pass
                # osc_client.send(mess)

            
            
        
        return True
        ##################################################
        # nothing happens below
        
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


    terms = list(chain(*[e['tags'] for e in infos.values()]))
    follows = [e['id_str'] for e in infos.values()]

    poll_candidates()
    
    try:
        stream.filter(track=terms, follow=follows)
    except KeyboardInterrupt:
        print('closed connection')
    finally:
        conn.close()
            


    
        
            


    
