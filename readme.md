# Inflating Egos

a project for isthisgood?

To get going:

`sqlite3 egos.db <create.sql`

Make a virtual environment:

`virtualenv -p python3`

and install dependencies:

`pip install -r requirements.txt`


### Tools

* `python create_data.py outfile=candidate_faces/data.json`

  Create a json data file with the contents of the SQLite database

* `python tsv2dict.py outfile=terms.py`

  Create the terms (hastags and handles) that the stream filters. Takes it's input from stdin terminated by an empty line. Normally, you paste a Google Doc spreadsheet into this.
