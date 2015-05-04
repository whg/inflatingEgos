from __future__ import print_function
import threading
import requests
from lxml import html
from pymongo import MongoClient
import time
import logging

from twitter_infos import infos
from osc_helpers import *

collection = None


def data_for_url(candidate):
    """
    candiate: item from infos dictionary
    """
    global collection
    
    if not collection:
         mongo = MongoClient()
         collection = mongo["egos"]["main2"]
    
    response = requests.get(candidate['url'])
    s = html.fromstring(response.text)

    ids = s.xpath('//*[@class="StreamItem js-stream-item"]/div/@data-item-id')
    users = s.xpath('//*[@class="StreamItem js-stream-item"]/div/@data-user-id')
    favourites = s.xpath('//*[@class="ProfileTweet-action--favorite u-hiddenVisually"]/span/@data-tweet-stat-count')
    retweets = s.xpath('//*[@class="ProfileTweet-action--retweet u-hiddenVisually"]/span/@data-tweet-stat-count')

    data = [ids, users, retweets, favourites]

    try :
        assert sum([float(len(e)) for e in data]) / 4 == len(ids)

        for id, user_id, retweets, favourites in zip(*data):

            rets = int(retweets)
            favs = int(favourites)
            
            if user_id != candidate['id_str']:
                logging.debug('wrong candidate id')
                continue
            
            query = { 'id_str' : id }
            cur = collection.find(query)
            
            if cur.count() > 0:
                doc = cur.next()

                favdiff = favs - doc['favorite_count']
                retdiff = rets - doc['retweet_count']

                collection.find_one_and_update(query, {
                    '$set': {
                        'retweet_count': rets,
                        'favorite_count': favs,
                    }
                })

                

                logging.debug('updated %s from %d (added %d) retweets, %d (added %d) favourites' % (id, rets, retdiff, favs, favdiff))

                yield (doc, retdiff, favdiff)

            else: #not in db, so instert a mini one
                collection.insert({
                    'id_str': id,
                    'retweet_count': int(rets),
                    'favorite_count': int(favourites),
                    'text': ' ',
                })
                logging.debug('inserted mini doc %s' % id)
                
        
    except AssertionError:
        logging.debug('mismatch in lengths')


def all_updates():
    for candidate_data in infos.values():
        for tweet_data, favs, rets in data_for_url(candidate_data):
            if favs > 10 or rets > 10:
                try:
                    message = personal_update(tweet_data, favs, rets)
                    send_message_to_screen(candidate_data['short_name'], message)
                    break
                except KeyError:
                    """There isn't text in the tweet data..."""
                    


def poll_candidates(t=10):
    def cb():
        while True:
            all_updates()
            time.sleep(t)
            
    thread = threading.Thread(target=cb)
    thread.daemon = True
    thread.start()
    logging.info('started poll_candidates thread')
    return thread
        
if __name__ == "__main__":
   


    urls = [e['url'] for e in infos.values()]

    for candidate in infos.values():
        data_for_url(candidate)

    # data_for_url('https://twitter.com/david_cameron')
