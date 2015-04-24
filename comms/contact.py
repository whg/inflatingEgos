from __future__ import print_function

import serial
import sys

us = True

if us:
    se = serial.Serial('/dev/cu.usbserial-A9ORRL9X')
else:
    class DummySerial():
        def close(self):
            pass
        def write(self, w):
            pass

    se = DummySerial()

def gc(c, n, t):
    return '?%s%s%s!' % (c, chr(n), chr(t))
    
def inflate(number, time=1):
    se.write(gc('i', number, time))

def deflate(number, time=1):
    se.write(gc('d', number, time))
    
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
    

try:
    while True:
        # input()
        i = raw_input()
        process(i)
except KeyboardInterrupt:
    sys.stdout.write('\rbye\n')
    sys.stdout.flush()
except SyntaxError as e:
    print(e)


    
    
se.close()
