import logging

conn = None

def construct_tweet(candidate, data, sentiment_func=None):
    """Make a dictionary to of the tweet + analysis + candidate"""
    
    row = {
        'id': data['id_str'],
        'tweet': data['text'],
        'posted_by': data['user']['name'],
        'timestamp': datetime.fromtimestamp(int(data['timestamp_ms']) / 1000.0),
        'candidate': candidate,
    }

    if sentiment_func:
        try:
            print(row['tweet'])
            sentiment = sentiment_func(data['text'])
            row.update(sentiment)
            print(sentiment)
        except:
            print("can't get sentiment")
            pass

    return row

mongo_col = None
def add_row_mongo(data):
    global mongo_col
    if not mongo_col:
        from pymongo import MongoClient
        mongo = MongoClient()
        mongo_col = mongo["egos"]["main2"]

    mongo_col.insert(data)
    logging.debug('inserted %s into mongo' % data['id'])
    
def add_row(row, table='tweets4'):
    """Given the json from a tweet and candidate add to the SQLite db
    :params:
    :candidate: this is the string from the keys of the  terms.py dict
    :data: a tweet in JSON
    """
    
    global conn
    
    names = ','.join(row.keys())
    marks = ','.join(['?' for _ in row])
    # table = 'tweets3'
    # table = 'raw_tweets'
    # table = 'logging'



    logging.debug(names)
    logging.debug(list(row.values()))

    qstring = 'INSERT INTO {table} ({names}) VALUES ({marks})'.format(**locals())

    try:
        conn.execute(qstring, list(row.values()))
        logging.info('inserted row into database')
    except sqlite3.IntegrityError as e:
        logging.info('bad values!')
        logging.info(e)
        
    conn.commit()

