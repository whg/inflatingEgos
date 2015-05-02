def get_sentiment2(text):
    url = "https://japerk-text-processing.p.mashape.com/sentiment/"

    headers = {
        "X-Mashape-Key": "MU1w0GGHA8mshaHMPY4wNap7sMmip1VvrhWjsnexOzYAM2UqEQ",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    params = {
        "language": "english",
        "text": text
    }


    r = requests.post(url, headers=headers, data=params)
    j = r.json()
    d = j['probability']
    d['label'] = j['label']
    return d



def get_sentiment(text):
    """Using TheySay to analyse a given text"""
    
    headers = { "Content-Type": "application/json" }
    url = "http://apidemo.theysay.io/api/v1/sentiment"
    r = requests.post(url, headers=headers, data=json.dumps({ 'text': text }))
    logging.info('made request, status code = %d' % r.status_code)
    return r.json()['sentiment']
