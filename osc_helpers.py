from pythonosc.udp_client import UDPClient
from pythonosc.osc_message_builder import OscMessageBuilder
import json
import re

from twitter_infos import infos

clients = {}

def osc_message(d):
    """
    create OSC message from a dict
    """
    msg = OscMessageBuilder(address = "/send")
    msg.add_arg(json.dumps(d))
    return msg.build()


def send_message(candidate, message):
    global clients
    if candidate not in clients:
        v = infos[candidate]
        if 'ip' not in v:
            print('no ip for %s' % (candidate))
            return
            
        clients[candidate] = UDPClient(v['ip'], v['osc_port'])

    clients[candidate].send(message)
    
    print('sent message to {0}'.format(candidate))
    
def assign_user(d, user):
    d['name'] = user['name']
    d['handle'] = user['screen_name']
    d['user-img-url'] = user['profile_image_url']
    
def tweet_message(data):

    # tweet = re.sub('http:/.+ ', '', data['text'])
    tweet = re.sub(r'http://[a-zA-Z0-9./…]+(?:\s+|$)', '', data['text'])
    
    arg = { 'tweet': tweet }
    
    if 'retweeted_status' in data:
        assign_user(arg, data['retweeted_status']['user'])
        arg['retweeted-by'] = data['user']['name']
        arg['tweet'] = data['text'].split(': ')[1]
        print("added retweet!!!!!!")
    else:
        assign_user(arg, data['user'])
    
    try:
        if 'media'in data['entities']:
            arg['media'] = data['entities']['media'][0]['media_url']
    except KeyError:
        pass

    
        
    return osc_message({
        'func': 'post',
        'arg': arg
    })

def personal_update(tweet, favs, retweets):
    return osc_message({
        'func': 'personal_update',
        'arg': {
            'tweet': tweet,
            'favourites': favs,
            'retweets': retweets
        }
    })
