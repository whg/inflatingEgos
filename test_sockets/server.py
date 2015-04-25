from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer

import argparse
import asyncio
import json
import threading

osc_server = None

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
            print('started osc server')
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()
    
    print('start.')
    server = WebSocketServerFactory("ws://localhost:9000", debug=False)
    MyServerProtocol.osc_ip = args.ip
    MyServerProtocol.osc_port = args.port
    server.protocol = MyServerProtocol
    
    
    loop = asyncio.get_event_loop()
    coro = loop.create_server(server, '127.0.0.1', 9000)
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

