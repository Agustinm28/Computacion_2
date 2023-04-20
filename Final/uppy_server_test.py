import socketserver
import argparse
from multiprocessing import Manager
import asyncio
import pickle

class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

class TCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print('[NEW CONNECTION] {} connected.'.format(self.client_address))

        file_pickle = self.request.recv(1024)
        file_obj = pickle.loads(file_pickle)
        filename = file_obj['filename']
        file_data = file_obj['data']
        print(f'[RECEIVING] File filename: {filename}')

        with open(filename, 'wb') as f:
            f.write(file_data)

        print(f'[SAVED] File saved as {filename}')
        self.request.close()

        #self.manager.queue.put(filename) # Agregamos el nombre de archivo a la cola compartida

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True, type=int, default=0, help='puerto del servidor')
    args = parser.parse_args()

    server(args)

def server(args):

    HOST, PORT = '127.0.0.1', args.port

    manager = Manager() # Creamos una cola compartida para comunicarse con los procesos hijos
    queue = manager.Queue()

    with ForkedTCPServer((HOST, PORT), TCPRequestHandler) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')

        while True:
            server.handle_request()

            # Verificamos si hay algún archivo en la cola compartida
            while not queue.empty():
                filename = queue.get()
                print(f'[PROCESSING] Processing file {filename}...')
                # Agregue su código aquí para procesar el archivo, como enviarlo a un modelo de aprendizaje automático para su análisis.

if __name__ == "__main__":
    main()

