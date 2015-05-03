# Inflating Egos

a project for isthisgood?

## Setup

Something like this:

`sudo pip install -r requirement.txt`

If you're on linux you may want to use `apt-get`, e.g. `sudo apt-get install python3-lxml`. Also maybe use a virtual environment?

For the stream, install mongoDB and get it running. Optionally install sqlite3.

## Usage

```python
usage: stream.py [-h] [-p P] [-b B]

optional arguments:
  -h, --help  show this help message and exit
  -p P        don't poll for retweets and favorites
  -b B        don't talk to the balloons
```

`stream.py` starts a Twitter stream, polls the candidate's pages for retweets and favourite counts. It also talks to the arduino that inflates the balloons. 

For each machine that displays the tweets. First `python3 -m http.server 80` in the root dir.

Then run something like `python server.py -c cameron`, from the client dir. This receives the tweets via OSC and sends them via websockets. Then open a browser and load `locahost/client/client.html#cameron`. Do the last two steps for the candidates you need on that machine. If `stream.py` is running then the web client will start receiving the tweets. Make sure the IPs are set correctly in `info.json`. 


## Old things

To get going:

`sqlite3 egos.db <create.sql`

Make a virtual environment:

`virtualenv -p python3`

and install dependencies:

`pip install -r requirements.txt`


#### Tools

* `python create_data.py outfile=candidate_faces/data.json`

  Create a json data file with the contents of the SQLite database

* `python tsv2dict.py outfile=terms.py`

  Create the terms (hastags and handles) that the stream filters. Takes it's input from stdin terminated by an empty line. Normally, you paste a Google Doc spreadsheet into this.x
