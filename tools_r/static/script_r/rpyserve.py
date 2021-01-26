import SocketServer
import sys
import subprocess

class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip().split(' ')

        # verbose server
        print "%s wrote:" % self.client_address[0]
    
        elements = ['Rscript'] + self.data
       # elements.append(self.data)

        print elements

        results = subprocess.call(elements)

        # return the result of the evaluation as a string
        # to the client
        self.wfile.write(str(results))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', 
                        type=int,
                        default=8080,
                        help='port')
    parser.add_argument('--hostname',
                        default='localhost')
    options = parser.parse_args()

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((options.hostname, options.port),
                                    MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()