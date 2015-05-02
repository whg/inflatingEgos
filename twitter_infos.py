"""
This file contains all the details for the candidates
actually, they are loaded from the JSON file so the web client can load them too
"""

import json
import os
infos = json.load(open(os.path.join(os.path.dirname(__file__), 'info.json')))


other_tags = [
    "#infeg",
    "#inflatenigel",
    "#inflatedavid",
    "#inflateed",
    "#inflatenick",
    "#inflateleanne",
    "#inflatenatalie",
    "#inflatenicola",
]
