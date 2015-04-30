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

from twitter_infos import infos, other_tags
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


    def on_data(self, data):
        """This is where all the magic happens"""

        if type(data) is str:
            data = json.loads(data)
            add_row_mongo(data)

        # global osc_client
        # if not osc_client:
        #     # osc_client = udp_client.UDPClient('192.168.0.83', 5005)
        #     osc_client = udp_client.UDPClient('localhost', 5005)
        # print("asdf")

        import re


        rexp = r'#infeg[a-z 1-9\-]+. '
        match = re.findall(rexp, data['text'])

        if match:
            logging.info('found match')
            try:
                vs = match[0].split()
                candidate = vs[1]
                amount = int(vs[2][:-1])
                logging.info('affecting candidate')
                data['text'] = re.sub(rexp, '', data['text'])
                affect_candidate(candidate, data, amount)
                
            except:
                logging.info('invalid instruction')

        
        for v in infos.values():
            r = '|'.join(v['tags'])
            
            if re.search(r, data['text'], re.IGNORECASE):
                candidate = v['short_name']                    
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

    # poll_candidates(10)

    
    
    terms.extend(other_tags)
    logging.info(terms)

    from pymongo import MongoClient
    mongo = MongoClient()
    mongo_col = mongo["egos"]["main"]
    import time
    from bson.json_util import dumps
    
    def go():
        i = 0
        offset = 20
        for doc in mongo_col.find({}):
            i+= 1
            if i < offset:
                continue

            try:
                if "#conservatives" in doc['text'].lower():
                    continue


                listener.on_data(doc)
                time.sleep(0.15)
            except KeyError:
                pass
            # i+= 1

            if i == offset + 18:
                # doc = mongo_col.find_one({'id_str': "591544172085178368"})
                # green
                doc = mongo_col.find_one({'id_str': "591629747945365504"})
                # snp
                # doc = mongo_col.find_one({'id_str': "591627649971281920"})
                # plaid
                # doc = mongo_col.find_one({'id_str': "591629747945365504"})
                
                # message = personal_update(doc, 37, 50)
                # send_message("cameron", message)
                print(doc)
                affect_candidate("bennett", doc, 1)

    ts = threading.Thread(target=go)
    # ts.start()

    # go()
    
    try:

        
        
        # go()
        # print('starting stream')
        stream.filter(track=terms, follow=follows)

        
        
    except KeyboardInterrupt:
        print('closed connection')
    finally:
        conn.close()
            


    
        
            


    
