from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
from pythonosc import dispatcher
from pythonosc.osc_server import ForkingOSCUDPServer, ThreadingOSCUDPServer
import asyncio
import json

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def send(self, ud, data):
        print('sending osc message to page')
        self.sendMessage(data.encode('utf8'))


    def onOpen(self):
        global server
        server = self

        print("WebSocket connection open.")
        
        dispatch = dispatcher.Dispatcher()
        dispatch.map("/send", self.send)

        print('osc starting...')
        server = ThreadingOSCUDPServer(('localhost', 9001), dispatch)
        server.serve_forever()
        

        
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
    

    print('start.')
    server = WebSocketServerFactory("ws://localhost:9000", debug=True)
    server.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(server, '127.0.0.1', 9000)
    connection = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()
        loop.close()


    # import sys

    # from twisted.python import log
    # from twisted.internet import reactor

    # log.startLogging(sys.stdout)

    # factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    # factory.protocol = MyServerProtocol
    # # factory.setProtocolOptions(maxConnections=2)

    # reactor.listenTCP(9000, factory)
    # reactor.run()
    
    # # socket_server = threading.Thread(target=start_socket_server)
    # print('started...')
    # while True:
    #     i = input()
    #     if i == 'q':
    #         break
