from pythonosc.osc_message_builder import OscMessageBuilder
import json

def osc_message(d):
    """
    create OSC message from a dict
    """
    msg = OscMessageBuilder(address = "/send")
    msg.add_arg(json.dumps(d))
    return msg.build()


def assign_user(d, user):
    d['name'] = user['name']
    d['handle'] = user['screen_name']
    d['user-img-url'] = user['profile_image_url']
    
def tweet_message(data):
    arg = {
        'tweet': data['text'],
    }
    
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

