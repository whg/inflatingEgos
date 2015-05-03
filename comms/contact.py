from __future__ import print_function

import serial
import sys
import threading
import queue
from time import sleep
import logging
import pickle

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

import sys
sys.path.append('..')

from twitter_infos import infos
import osc_helpers as oh


balloon_queue = None

us = False
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
        'number': 0,
        'size': 0
    },
    'cameron': { 'number': 5, 'size': 0 },
    'clegg': { 'number': 2, 'size': 0 },
    'miliband': { 'number': 3, 'size': 0 },
    'wood': { 'number': 4, 'size': 0 },
    'sturgeon': { 'number': 1, 'size': 0 },
    'bennett': { 'number': 6, 'size': 0 },
}


def gc(c, n, t=0):
    s = '?%s%s%s!' % (c, chr(n), chr(t))
    return bytes(s, 'utf-8')
    
def inflate(number, time=1):
    se.write(gc('i', number, time))

def deflate(number, time=1):
    se.write(gc('d', number, time))

def stop(number):
    se.write(gc('s', number))
    
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

def balloon_size(ud, number, area, circleness):
    logging.debug("got ballon data for %d" % (number))
    
    for candidate, value in candidates.items():
        if value['number'] == number:
            # if circleness > 0.8:
            candidates['size'] = area
            logging.debug("set size for %s to %f" % (candidate, area))

            # stop a balloon staying on deflate for too long
            if area < infos[candiate]['min_inflation']:
                stop(number)
                
            return


def start_connection():

    global se
    if us:
        se = serial.Serial('/dev/tty.usbserial-A403999Z')
    else:
        se = DummySerial()

    
    dispatch = dispatcher.Dispatcher()
    dispatch.map("/instruction", instruction)
    dispatch.map("/balloon", balloon_size)
    
    port = 5005
    osc_server = ForkingOSCUDPServer(('0.0.0.0', port), dispatch)
    server_thread = threading.Thread(target=osc_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print('started osc server on port %s' % port)
    
    return server_thread



def process_instruction(bi):

    # print("JASDJFSKDJ SFJDFS SDFJ")
    
    number = candidates[bi.candidate]['number']
    time = bi.amount
    
    sleep(1)
    print('ident = %s' % threading.current_thread().ident)

    oh.send_message_to_screen(bi.candidate, pickle.loads(bi.osc_msg))
    logging.info("process_instruction(): sent instruction to candidate")

    print('doing instruction')
    if time == 0:
        stop(number)
    elif time > 0:
        logging.debug('inflating %d for %d' % (number, time))
        inflate(number, time)
        sleep(time)
        logging.debug('done inflating %d' % (number))
    elif time < 0:
        logging.debug('deflating %d for %d' % (number, time))
        deflate(number, -time) # -time because it's negative if we get here
        sleep(-time)
        logging.debug('done inflating %d' % (number))

            
def balloon_worker():
    # pass
    global balloon_queue
    while True:
        # print('waiting for task...')
        if len(balloon_queue) > 0:
        # balloon_instruction = balloon_queue.get()
            process_instruction(balloon_queue[0])
            process_queue.pop(0)
        # balloon_queue.task_done()
        
        
def start_balloon_thread():

    global balloon_queue
    
    balloon_queue = [] #queue.Queue()
    print("made balloon queue")
    
    balloon_thread = threading.Thread(target=balloon_worker)
    balloon_thread.daemon = True
    balloon_thread.start()


    # q_manager_thread = QueueChecker(balloon_queue)
    # q_manager_thread.start()


    
if __name__ == "__main__":
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


