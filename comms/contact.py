from __future__ import print_function

import serial
import sys
import threading
import time

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

us = True

candidate_numbers = {
    'farage': 0,
    'cameron': 1,
    'clegg': 2,
    'miliband': 3,
    'wood': 4,
    'sturgeon': 5,
    'bennett': 6,
}

if us:
    se = serial.Serial('/dev/tty.usbserial-A403999Z')
else:
    class DummySerial():
        def close(self):
            pass
        def write(self, w):
            pass

    se = DummySerial()

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

    number = candidate_numbers[candidate]
    # time = args[1]

    time.sleep(5)
    
    if time == 0:
        stop(number)
    elif time > 0:
        inflate(number, time)
    elif time < 0:
        deflate(number, -time)

    print("------ instruction %s with %d" % (number, time))

if __name__ == "__main__":
    try:

        dispatch = dispatcher.Dispatcher()
        dispatch.map("/instruction", instruction)

        port = 5005
        osc_server = ForkingOSCUDPServer(('localhost', port), dispatch)
        server_thread = threading.Thread(target=osc_server.serve_forever)
        server_thread.start()
        print('started osc server on port %s' % port)

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
