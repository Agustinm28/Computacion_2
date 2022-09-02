import socketserver as ss
import argparse
import pickle as p
import sys
import math
from subprocess import Popen, PIPE


class ThreadingTCPServer(ss.ThreadingMixIn, ss.TCPServer):
    pass


class ForkingTCPServer(ss.ForkingMixIn, ss.TCPServer):
    pass


class TCPRequestHandler(ss.BaseRequestHandler):

    def handle(self):

        print(f'Conexión establecida con {self.client_address}.\n')

        while True:
            self.data = p.loads(self.request.recv(4096)).strip()
            print(f'{self.client_address} escribió: "{self.data}"\n')
            terminal = Popen(self.data, stdout=PIPE, stderr=PIPE, shell=True)
            out, err = terminal.communicate()

            if self.data == 'exit':
                self.request.sendall(p.dumps(f'GOODBYE\n'))
                print(f'Finalizando conexión con {self.client_address}.\n')
                exit(0)

            elif err.decode('utf-8') == '':
                out = out.decode("utf-8")

                if sys.getsizeof(out) > 4096:

                    self.request.send(
                        p.dumps('OK\n\n-----------------------------\n'))

                    for i in range(1, math.ceil(len(out) / 4047) + 1):
                        pack = out[4047 * (i - 1):4047 * i:]
                        self.request.send(p.dumps(f'{pack}'))

                    self.request.send(
                        p.dumps('-----------------------------\nEOF'))

                else:
                    self.request.sendall(p.dumps(
                        f'OK\n\n-----------------------------\n{out}-----------------------------\nEOF'))

            else:
                self.request.sendall(
                    p.dumps(f'ERROR\n\n{err.decode("utf-8")}'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int,
                        default=0, help='puerto del servidor')
    parser.add_argument('-c', '--conc', required=True, choices=[
                        'p', 't'], help='tipo de concurrencia: multi-process (p), multi-threads (t)')
    args = parser.parse_args()

    server(args)


def server(args):

    HOST, PORT = 'localhost', args.port
    options = {'t': ss.ThreadingTCPServer, 'p': ss.ForkingTCPServer}

    with options.get(args.conc)((HOST, PORT), TCPRequestHandler) as server:
        print(
            f'Server "{HOST}" ({server.server_address[0]}) hosteado en {server.server_address[1]}.')
        print('Esperando conexiones...\n')

        server.serve_forever()


if __name__ == "__main__":
    main()
