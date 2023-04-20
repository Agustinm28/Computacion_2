import socketserver
import argparse
from multiprocessing import Manager
import pickle
import os
from queue import Queue
import time

manager = Manager()  # Creamos una cola compartida para comunicarse con los procesos hijos
queue = manager.Queue()

class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


class TCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        BUFFER_SIZE = 1024 * 1024
        print('[NEW CONNECTION] {} connected.'.format(self.client_address))

        # Leer la longitud del objeto serializado
        # file_pickle_size_bytes = self.request.recv(4)
        # file_pickle_size = struct.unpack('!I', file_pickle_size_bytes)[0]
        # print(f'[READING] File size: {file_pickle_size}')

        # Leer el objeto serializado completo
        print(f'[READING] Reading searialized object')
        file_pickle = b''
        while True:
            data = self.request.recv(BUFFER_SIZE)
            if not data:
                break
            file_pickle += data
        print(f'[READING] Serialized object readed')

        # Deserializar el objeto
        file_obj = pickle.loads(file_pickle)
        print(f'[SERIALIZATION] Object deserialized')

        # Leer el archivo completo
        #file_size = file_obj['size']
        file_data = b''
        print(f'[READING] Reading file')
        while True:
            data = self.request.recv(BUFFER_SIZE)
            if not data:
                break
            file_data += data

        # Escribir el archivo en el disco
        filename = file_obj['filename']
        file_data = file_obj['data']
        print(f'[SAVING] Saving file locally')
        os.makedirs('./rec_files/', exist_ok=True)
        with open('./rec_files/' + filename, 'wb') as f:
            f.write(file_data)
        print(f'[SAVED] File saved as {filename}')
        self.request.close()

        print(f'[PROCESSING] Sending to queue')
        queue.put_nowait(filename)

        #self.manager.queue.put(filename) # Agregamos el nombre de archivo a la cola compartida


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True,
                        type=int, default=0, help='puerto del servidor')
    args = parser.parse_args()

    server(args)

def check_queue():
    if not queue.empty():
        return queue.get_nowait()

def server(args):

    HOST, PORT = '127.0.0.1', args.port

    with ForkedTCPServer((HOST, PORT), TCPRequestHandler) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')

        while True:
            server.handle_request()
            print(f'[PROCESSING] In queue')

            # Verificamos si hay algún archivo en la cola compartida
            time.sleep(1) #! Solucion temporal
            while not queue.empty():
                filename = queue.get_nowait()
                print(f'[PROCESSING] Processing file {filename}...')
                # Agregue su código aquí para procesar el archivo, como enviarlo a un modelo de aprendizaje automático para su análisis.

if __name__ == "__main__":
    main()
