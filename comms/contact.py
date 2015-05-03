from __future__ import print_function

import serial
import sys
import threading
from time import sleep
import logging

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

import sys
sys.path.append('..')

from twitter_infos import infos

us = False
class DummySerial():
    def close(self):
        pass
    def write(self, w):
        pass


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
    
def process(command):
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
    
        
def instruction(ud, candidate, time):

    number = candidates[candidate]['number']
    # time = args[1]

    sleep(5)
    
    if time == 0:
        stop(number)
    elif time > 0:
        inflate(number, time)
    elif time < 0:
        deflate(number, -time)

    logging.debug("instruction %s with %d" % (number, time))


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

if __name__ == "__main__":
    try:

        start_connection()

        while True:
            # input()
            i = input()
            process(i)
    except KeyboardInterrupt:
        sys.stdout.write('\rbye\n')
        sys.stdout.flush()
    except SyntaxError as e:
        print(e)
    
    finally:
        se.close()


