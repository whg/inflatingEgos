from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

import argparse
import asyncio
import json
import threading

osc_server = None

import sys
sys.path.append('..')

class MyServerProtocol(WebSocketServerProtocol):
    osc_ip = None
    osc_port = None
    
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def send(self, ud, data):
        print('sending osc message to page' + data)
        self.sendMessage(data.encode('utf8'), False)

        
    def onOpen(self):
        print("WebSocket connection open.")
        
        dispatch = dispatcher.Dispatcher()
        dispatch.map("/send", self.send)


        global osc_server
        if not osc_server:
            osc_server = ForkingOSCUDPServer((self.osc_ip, self.osc_port), dispatch)
            server_thread = threading.Thread(target=osc_server.serve_forever)
            server_thread.start()
            print('started osc server on port %s' % self.osc_port)
        else:
            osc_server._dispatcher = dispatch
            print('osc server already running, reset dispatcher')
        
        
    def onMessage(self, payload, isBinary):
        # import IPython; IPython.embed()
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))



coro = None
import twitter_infos as ti

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", default="cameron", help="candidate name")
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    # parser.add_argument("--port",type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    cid = ti.inverse[args.c]
    port = ti.infos[cid]['ws_port']
    
    print('starting for {0} on {1}'.format(args.c, port))
    server = WebSocketServerFactory("ws://localhost:{0}".format(port), debug=False)
    MyServerProtocol.osc_ip = args.ip
    MyServerProtocol.osc_port = ti.infos[cid]['osc_port']
    server.protocol = MyServerProtocol
    
    
    loop = asyncio.get_event_loop()
    coro = loop.create_server(server, '127.0.0.1', port)
    # future = next(coro)
    connection = loop.run_until_complete(coro)
    # import IPython; IPython.embed()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()
        loop.close()
        osc_server.shutdown()

