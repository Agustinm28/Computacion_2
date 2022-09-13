from asyncio import subprocess
import socketserver as ss
import socket
import argparse
import pickle as p
import sys
import math
from subprocess import Popen, PIPE
import subprocess


class ThreadingTCPServer(ss.ThreadingMixIn, ss.TCPServer):
    pass


class ForkingTCPServer(ss.ForkingMixIn, ss.TCPServer):
    pass


class TCPRequestHandler(ss.BaseRequestHandler):

    def handle(self):

        FORMAT = 'utf-8'
        HEADER = 64
        DISCONNECT_MESSAGE = '!DISCONNECT'
        print(f'[NEW CONNECTION] {self.client_address} connected.')

        while True:
            msg_len = self.request.recv(HEADER).decode(FORMAT)
            if msg_len:
                msg_len = int(msg_len)
                command = self.request.recv(msg_len).decode(FORMAT)
                if command == DISCONNECT_MESSAGE or command == 'exit':
                    print(DISCONNECT_MESSAGE)
                    break
                
                print(f'[{self.client_address}] > Command {command} Executed')
                output = 'output: \n'
                output += subprocess.getoutput(command)
                self.request.send(output.encode(FORMAT))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=0, help='puerto del servidor')
    parser.add_argument('-c', '--conc', required=True, choices=['p', 't'], help='tipo de concurrencia: multi-process (p), multi-threads (t)')
    args = parser.parse_args()

    server(args)


def server(args):

    HOST, PORT = 'localhost', args.port
    options = {'t': ss.ThreadingTCPServer, 'p': ss.ForkingTCPServer}

    with options.get(args.conc)((HOST, PORT), TCPRequestHandler) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}')

        server.serve_forever()


if __name__ == "__main__":
    main()

