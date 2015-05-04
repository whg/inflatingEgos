from __future__ import print_function

import serial
import sys
import threading
import queue
from time import sleep
import logging
import pickle
from collections import defaultdict
import sqlite3 as lite

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

import sys
sys.path.append('..')

from twitter_infos import infos
import osc_helpers as oh

logging.basicConfig(level=logging.INFO)

import queue
lock = threading.Lock()
callback_queue = queue.Queue()

balloon_queue = None
db_con = None

us = True
class DummySerial():
    def close(self):
        pass
    def write(self, w):
        pass


class BalloonInstruction(object):
    def __init__(self, candidate, amount, osc_msg):
        self.candidate = candidate
        self.amount = amount
        self.osc_msg = osc_msg
        
candidates = {
    'farage': {
        'number': 6,
        'size': 0,
        'wanted': 0.14
    },
    'cameron': { 'number': 5, 'size': 0, 'wanted': 0.33 },
    'clegg': { 'number': 4, 'size': 0, 'wanted': 0.08 },
    'miliband': { 'number': 3, 'size': 0, 'wanted': 0.33 },
    'wood': { 'number': 43, 'size': 0, 'wanted': 0.0 },
    'sturgeon': { 'number': 2, 'size': 0, 'wanted': 0.06 },
    'bennett': { 'number': 1, 'size': 0, 'wanted': 0.06 },
}

statuses = defaultdict(bool)

def gc(c, n, t=0):
    s = '?%s%s%s!' % (c, chr(n), chr(t))
    return bytes(s, 'utf-8')
    
def inflate(number, time=1):
    se.write(gc('i', number, time))
    statuses[number] = True

def deflate(number, time=1):
    se.write(gc('d', number, time))
    statuses[number] = True

def stop(number):
    se.write(gc('s', number))
    statuses[number] = False
    
def process_text_input(command):
    tokens = command.split()
    if len(tokens) < 2:
        print('need 2 tokens')
        return

    func = tokens[0]
    number = int(tokens[1])
    time = 1
    if len(tokens) > 2:
        time = int(tokens[2])
    

    if func in locals():
        locals()[func](number, time)
    elif func == 'i':
        inflate(number, time)
    elif func == 'd':
        deflate(number, time)
    
        
def instruction(ud, candidate, time, osc_msg):
    global balloon_queue
    
    # time = args[1]
    logging.debug("queueing osc instruction %s with %d" % (candidate, time))

    # print("queue size = %d" % len(balloon_queue))

    # balloon_queue.append(BalloonInstruction(candidate, time, osc_msg))

    # print("queue size = %d" % len(balloon_queue))
    # balloon_queue.join()

    
    process_instruction(BalloonInstruction(candidate, time, osc_msg))


def balloon_size2(number, area, circleness):

    global candidates
    global db_con

    c = None
    for candidate, value in candidates.items():
        if value['number'] == number:
            c = candidate
            break

    try:
        if c:
            cur = db_con.cursor()
            cur.execute('UPDATE sizes SET size=? WHERE name=?', (area, candidate))
            db_con.commit()
            logging.debug("set size for %s (%d) to %f" % (candidate, number, area))

        else:
            print('cant find candidate')
    except lite.DatabaseError:
        pass

def balloon_size(ud, number, area, circleness):
    
    # print('bs')
    balloon_size2(number, area, circleness)
    return

    global candidates

    global db_con
    global lock
    print(candidates)

    for candidate, value in candidates.items():
        if value['number'] == number:
            # if circleness > 0.8:
            c = candidate
            print('c = %s, s = %d' % (candidate, area))
            candidates[candidate]['size'] = area
            return



def start_connection():

    global se
    if us:
        se = serial.Serial('/dev/ttyUSB0')
    else:
        se = DummySerial()

    
    global db_con
    db_con = lite.connect('sizes.db')

    
    dispatch = dispatcher.Dispatcher()
    dispatch.map("/instruction", instruction)
    dispatch.map("/balloon", balloon_size)
    dispatch.map("/adjust", adjust_balloons)
    
    port = 5005
    osc_server = ForkingOSCUDPServer(('0.0.0.0', port), dispatch)
    # server_thread = threading.Thread(target=osc_server.serve_forever)
    # server_thread.daemon = True
    # server_thread.start()
    print('started osc server on port %s' % port)
    osc_server.serve_forever()
    

def size_for_candidate(candidate):
    global db_con
    try:
        cur = db_con.cursor()
        logging.info('candidate = %s' % candidate)
        # cur.execute('SELECT size from sizes WHERE name=?', (candidate,))
        cur.execute("select size from sizes where name='%s'" % candidate)
        row = cur.fetchone()
        return row[0]
    except:
        return -1

def adjust_balloons(ud):
    global candidates
    logging.info('adjusting')
    # print(candidates)
    for candidate, v in candidates.items():
        size = size_for_candidate(candidate)
        logging.info('adjusting %s' % candidate)
        if size < 0:
            continue
        number = v['number']
        time = 25
        if size < 20000 * v['wanted']:
            logging.debug('inflating %d for %d' % (number, time))
            inflate(number, time)
            sleep(time * 0.1)
            stop(number) # just for good measure
            logging.debug('done inflating %d' % (number))
        else:
            logging.debug('deflating %d for %d' % (number, time))
            deflate(number, time) # -time because it's negative if we get here
            sleep(time * 0.1)
            stop(number) # just for good measure
            logging.debug('done inflating %d' % (number))

def process_instruction(bi):
    
    global candidates
    number = candidates[bi.candidate]['number']
    time = bi.amount * 10

    oh.send_message_to_screen(bi.candidate, pickle.loads(bi.osc_msg))
    logging.info("process_instruction(): sent instruction to candidate")

    size = size_for_candidate(bi.candidate)
    if size < 0:
        return

    if size > 19000:
        return
    sleep(5)
    print('ident = %s' % threading.current_thread().ident)

    
    print('doing instruction')
    if time == 0:
        stop(number)
    elif time > 0:
        logging.debug('inflating %d for %d' % (number, time))
        inflate(number, time)
        sleep(time * 0.1)
        stop(number) # just for good measure
        logging.debug('done inflating %d' % (number))
    elif time < 0:
        logging.debug('deflating %d for %d' % (number, time))
        deflate(number, -time) # -time because it's negative if we get here
        sleep(-time * 0.1)
        stop(number) # just for good measure
        logging.debug('done inflating %d' % (number))

                
if __name__ == "__main__":

    # start_connection()
    # cand = candidates['clegg']
    # while cand['size'] < 2000:
    #     inflate(cand['number'], 10)
    #     sleep(5)
    #     print(cand['size'])

    # exit()

    try:



        start_connection()

        while True:
            i = input()
            process_text_input(i)
    except KeyboardInterrupt:
        sys.stdout.write('\rbye\n')
        sys.stdout.flush()
    except SyntaxError as e:
        print(e)
    
    finally:
        se.close()


