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
from argparse import ArgumentParser
import re

from twitter_infos import infos, other_tags
import osc_helpers as oh
from comms import contact

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
        

    def on_data(self, data):
        """This is where all the magic happens"""

        # might be emulatin twitter by pulling from mongo,
        # so don't re-add 
        if type(data) is str:
            data = json.loads(data)
            add_row_mongo(data)

        # print(data)


        rexp = r'#infeg[a-z 1-9\-]+. '
        instruction_match = re.findall(rexp, data['text'])

        if instruction_match:
            logging.info('found match')
            try:
                vs = instruction_match[0].split()
                candidate = vs[1]
                amount = int(vs[2][:-1])
                logging.info('affecting candidate')
                data['text'] = re.sub(rexp, '', data['text'])
                oh.affect_candidate(candidate, data, amount)
                
            except Exception as e:
                logging.info('invalid instruction')
                print(e)

            
        cumulative = defaultdict(int)
        
        for candidate, v in infos.items():
            # try:
            #     tagstring = v['tagstring']
            # except KeyError:
            #     tagstring = '|'.join(v['tags'].keys())
            #     v['tagstring'] = tagstring
                
            
            # if re.search(tagstring, data['text'], re.IGNORECASE):
            #     mess = oh.tweet_message(data)
            #     oh.send_message_to_screen(candidate, mess)

            for tag, weight in v['tags'].items():
                if re.search(tag, data['text'], re.IGNORECASE):
                    # oh.send_message(candidate, oh.tweet_message(data))

                    cumulative[candidate]+= weight
                    logging.debug('found {tag} in {candidate}'.format(**locals()))
                    # logging.debug('%s size = %f' % (candidate, contact.candidates[candidate]['size']))
            # logging.info(data['text'])
        logging.debug(cumulative)

        # let's only use this when one candidate is mentioned.
        if len(cumulative) == 1:
            # i think this is the easiest way to get the item
            for candidate, count in cumulative.items():
                if count > 0:
                    logging.debug("going for affect candidate")
                    oh.affect_candidate(candidate, data, count)

        
        return True

    def on_error(self, status):
        print(status)

    def on_exception(self, e):
        # import IPython
        # IPython.embed()
        print(e)
        

def analyse_tweets(candidate, handle, filename, table):
    """Load tweets from the filename and save to the db with the sentiment analysis"""
    import time

    data = json.loads('[' + open(filename).read()[:-2] + ']')
    
    for d in data:
        if handle in d['text']:
            row = oh.construct_tweet(candidate, d, get_sentiment)
            add_row(row, table)
            time.sleep(0.1)
        

        
if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", dest="polling", action="store_false", help="don't poll for retweets and favorites")
    parser.add_argument("-b", dest="balloon", action="store_false", help="don't talk to the balloons")
    parser.set_defaults(polling=True, balloon=True)
    args = parser.parse_args()
    
    # conn = sqlite3.connect('egos.db')
    # analyse_tweets('cameron', '@David_Cameron', '/Users/whg/Desktop/10k_tweets', 'cameron')
    # exit()
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    listener = InflatedEgos()
    stream = Stream(auth, listener)


    terms = list(chain(*[e['tags'].keys() for e in infos.values()]))
    follows = [e['id_str'] for e in infos.values()]


    terms.extend(other_tags)
    logging.info(terms)



    try:
        if args.polling:
            poll_thread = poll_candidates(10)
        
        # if args.balloon:
        #     contact_thread = contact.start_connection()
            # contact.start_balloon_thread()
        
        stream.filter(track=terms, follow=follows)

        
    except KeyboardInterrupt:
        print('closed connection')
    finally:
        # conn.close()
        if contact_thread:
            contact_thread.join()

        # if poll_thread:
        #     poll_thread.join()

        pass
