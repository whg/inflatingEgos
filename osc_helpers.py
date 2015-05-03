from pythonosc.udp_client import UDPClient
from pythonosc.osc_message_builder import OscMessageBuilder
import logging
import json
import re

from twitter_infos import infos

clients = {}

def osc_message(d):
    """
    create OSC message from a dict
    """
    msg = OscMessageBuilder(address="/send")
    msg.add_arg(json.dumps(d))
    return msg.build()


def send_message(candidate, message):
    global clients
    if candidate not in clients:
        v = infos[candidate]
        if 'ip' not in v:
            logging.debug('no ip for %s' % (candidate))
            return
            
        clients[candidate] = UDPClient(v['ip'], v['osc_port'])

    clients[candidate].send(message)
    
    logging.debug('sent message to {0}'.format(candidate))
    
def assign_user(d, user):
    d['name'] = user['name']
    d['handle'] = user['screen_name']
    d['user-img-url'] = user['profile_image_url']


def tweet_arg(data):
    tweet = re.sub(r'(http|https)://[a-zA-Z0-9./…]+(?:\s+|$)', '', data['text'])
    
    arg = { 'tweet': tweet }
    
    if 'retweeted_status' in data:
        assign_user(arg, data['retweeted_status']['user'])
        arg['retweeted-by'] = data['user']['name']
        arg['tweet'] = data['text'].split(': ')[1]
        # print("added retweet!!!!!!")
    else:
        assign_user(arg, data['user'])
    
    try:
        if 'media'in data['entities']:
            arg['media'] = data['entities']['media'][0]['media_url']
    except KeyError:
        pass

    return arg
        
def tweet_message(data):
    
    arg = tweet_arg(data)
        
    return osc_message({
        'func': 'post',
        'arg': arg
    })

def personal_update(tweet_data, favs, retweets):
    arg = tweet_arg(tweet_data)
    arg['favourites'] = favs
    arg['retweets'] = retweets
    return osc_message({
        'func': 'personal_update',
        'arg': arg
    })


def action_update(tweet_data, amount):
    arg = tweet_arg(tweet_data)
    arg['amount'] = amount
    return osc_message({
        'func': 'action_update',
        'arg': arg
    })
    
balloon_osc = None
    
def affect_candidate(candidate, tweet_data, amount):
    global balloon_osc
    if not balloon_osc:
        balloon_osc = UDPClient('localhost', 5005)


    msg = OscMessageBuilder("/instruction")
    msg.add_arg(candidate)
    msg.add_arg(amount)
    balloon_osc.send(msg.build())
    logging.info("sent instruction %s, %d" % (candidate, amount))

    send_message(candidate, action_update(tweet_data, amount))
    logging.info("sent instruction to candidate")



    
