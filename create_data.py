import json
import sqlite3
import sys

out = sys.argv[1] if len(sys.argv) > 1 else 'candidate_faces/data.json'

conn = sqlite3.connect('egos.db')

labels = ['tweet', 'candidate', 'label', 'positive', 'negative', 'confidence']
q = conn.execute('select %s from tweets3;' % ','.join(labels))
vals = q.fetchall()

data = [dict(zip(labels, v)) for v in vals]

json.dump(data, open(out, 'w'))

conn.close()
