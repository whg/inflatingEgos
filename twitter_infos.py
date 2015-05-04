"""
This file contains all the details for the candidates
actually, they are loaded from the JSON file so the web client can load them too
"""

import json
import os
infos = json.load(open(os.path.join(os.path.dirname(__file__), 'info.json')))

other_tags = [
    "#infeg",
]

special_tags = [
    ( "farage", "#inflatenigel" ),
    ( "cameron", "#inflatedavid" ),
    ( "miliband", "#inflateed" ),
    ( "clegg", "#inflatenick" ),
    ( "wood", "#inflateleanne" ),
    ( "bennett", "#inflatenatalie" ),
    ( "sturgeon", "#inflatenicola" ),
]

for cand, tag in special_tags:
    other_tags.append(tag)

def filename2words_re(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        swear_lines = f.readlines()
        swear_words = [' ' + line.strip() + ' ' for line in swear_lines]
    return '|'.join(swear_words)
        

swear_re = filename2words_re('data/swear_words.txt')
neg_re = filename2words_re('data/neg_words.txt')
