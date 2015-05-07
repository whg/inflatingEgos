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
import sys

from twitter_infos import infos, other_tags, swear_re, neg_re, special_tags
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

last_update = {}

def do_affect(candidate, data, count, force=False):
    space = 25
    
    now = datetime.now()

    try:
        delta = (now - last_update[candidate]).seconds
    except KeyError:
        from random import randint
        delta = space +1
        
    if delta > space or force:
        logging.info('sending affect to %s' % candidate)
        osc_msg = oh.action_update(data, count)
        oh.affect_candidate(candidate, osc_msg, count)
        last_update[candidate] = now
    else:
        logging.info('not enough space between')
        
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
            # add_row_mongo(data)


        if 'text' not in data:
            return
            
        tweet = data['text']

        ###################################################
        ## twitter instructions using #infeg
        
        rexp = r'#infeg[a-z 0-9\-]+. '
        instruction_match = re.findall(rexp, tweet)

        if instruction_match:
            logging.info('found match')
            try:
                vs = instruction_match[0].split()
                logging.info('asdf %s' % vs)
                candidate = vs[1]
                amount = int(vs[2][:-1])
                logging.info('affecting candidate')
                tweet = re.sub(rexp, '', tweet)
                osc_msg = oh.action_update(data, amount)
                oh.affect_candidate(candidate, osc_msg, amount)
                
            except Exception as e:
                logging.info('invalid instruction')
                raise e


        ######################################################
        ## special tags

        for candidate, tag in special_tags:
            if tag in tweet:
                do_affect(candidate, data, 5, force=True)

        ######################################################
        ## find the tags that mean something
        
        cumulative = defaultdict(int)
        
        for candidate, v in infos.items():

            try:
                tagstring = v['tagstring']
            except KeyError:
                tagstring = '|'.join(v['tags'].keys())
                v['tagstring'] = tagstring


            if re.search(tagstring, data['text'], re.IGNORECASE):
                mess = oh.tweet_message(data)
                oh.send_message_to_screen(candidate, mess)
            

            for tag, weight in v['tags'].items():
                if re.search(tag, tweet, re.IGNORECASE):
                    # oh.send_message(candidate, oh.tweet_message(data))


                    # tag_pos = tweet.find(tag)
                    # if tag_pos == 0:
                    #     continue
                        
                    # prev_word = tweet[:tag_pos].split()[-1]
                    # if re.search(neg_re, prev_word, re.IGNORECASE):
                    #     continue
                        
                    cumulative[candidate]+= weight
                    
        ######################################################
        ## dispatch the tweets accordingly
        ## if 
        print(cumulative)
        
        for candidate, count in cumulative.items():
            if count != 0:
                # # make sure the tag isn't negated
                # if not re.search(neg_re, tweet, re.IGNORECASE):
                #     logging.info("going for affect %s" % candidate)
                #     logging.info(tweet)

                logging.info(tweet)
                do_affect(candidate, data, count)
                # osc_msg = oh.action_update(data, count)
                # oh.affect_candidate(candidate, osc_msg, count)
            else:
                pass

            handle_re = [k for k in infos[candidate]['tags'].keys() if '@' in k]
                # only do for handles
            if re.search('|'.join(handle_re), tweet, re.IGNORECASE):
                # let's have a swear word
                print('in handle')
                if re.search(swear_re, tweet, re.IGNORECASE):
                    count = -5
                    do_affect(candidate, data, count)
                    # osc_msg = oh.action_update(data, count)
                    # oh.affect_candidate(candidate, osc_msg, count)
                    print("BIG SWEAR WORD!!!!!!!!!!!!!")
                    logging.info(tweet)

        
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
    parser.add_argument("-e", dest="emulate", action="store_true", help="emulate from database")
    parser.set_defaults(polling=True, balloon=True, emulate=False)
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

    def adjust_thread():
        while True:
            oh.adjust_balloons()
            time.sleep(19)

    adjust_thread = threading.Thread(target=adjust_thread)
    adjust_thread.daemon = True

    try:
        if args.emulate:
            from pymongo import MongoClient
            mongo = MongoClient()
            mongo_col = mongo["egos"]["main2"]
            for doc in mongo_col.find({}):
                listener.on_data(doc)
                time.sleep(0.2)
            
        else:
            if args.polling:
                poll_thread = poll_candidates(10)
            
            adjust_thread.start()
        # if args.balloon:
        #     contact_thread = contact.start_connection()
            # contact.start_balloon_thread()
        
        stream.filter(track=terms, follow=follows)

        
    except KeyboardInterrupt:
        print('closed connection')
        sys.exit(0)
    finally:
        # conn.close()
        # if contact_thread:
        #     contact_thread.join()

        # if poll_thread:
        #     poll_thread.join()

        pass

    sys.exit(1)
