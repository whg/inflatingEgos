from __future__ import print_function
from threading import Thread
import requests
from lxml import html
from pymongo import MongoClient

from twitter_infos import infos

collection = None


def data_for_url(candidate):
    """
    candiate: item from infos dictionary
    """
    
    response = requests.get(candidate['url'])
    s = html.fromstring(response.text)

    ids = s.xpath('//*[@class="StreamItem js-stream-item"]/div/@data-item-id')
    users = s.xpath('//*[@class="StreamItem js-stream-item"]/div/@data-user-id')
    favourites = s.xpath('//*[@class="ProfileTweet-action--favorite u-hiddenVisually"]/span/@data-tweet-stat-count')
    retweets = s.xpath('//*[@class="ProfileTweet-action--retweet u-hiddenVisually"]/span/@data-tweet-stat-count')

    data = [ids, users, retweets, favourites]
    # extracted = [d.extract() for d in data]

    try :
        assert sum([float(len(e)) for e in data]) / 4 == len(ids)

        for id, user_id, retweets, favourites in zip(*data):

            rets = int(retweets)
            favs = int(favourites)
            
            if user_id != candidate['id_str']:
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
# /                print('updated', id, 'to', rets, ' ()retweets and', favs, 'favourites')
                print('updated %s from %d (added %d) retweets, %d (added %d) favourites' %
                      (id, rets, retdiff, favs, favdiff)
        
    except AssertionError:
        print('mismatch in lengths')


if __name__ == "__main__":
    mongo = MongoClient()
    collection = mongo["egos"]["main"]


    urls = [e['url'] for e in infos.values()]

    for candidate in infos.values():
        data_for_url(candidate)

    # data_for_url('https://twitter.com/david_cameron')
