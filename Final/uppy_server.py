import re
import socket
import socketserver
import argparse
from multiprocessing import Manager
import pickle
import os
import sys
from queue import Queue
from tqdm import tqdm
import multiprocessing
import mimetypes
from telegram_sender import send_file, send_message
from upscaler import scale_image, scale_image_ia, scale_video

# Servidor del bot, encargado de recibir los archivos y procesarlos

manager = Manager()  # Creamos una cola compartida para comunicarse con los procesos hijos
queue = manager.Queue()


class ForkedTCPServer4(socketserver.ForkingMixIn, socketserver.TCPServer):
    address_family = socket.AF_INET
    pass

class ForkedTCPServer6(socketserver.ForkingMixIn, socketserver.TCPServer):
    address_family = socket.AF_INET6
    pass


class TCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        BUFFER_SIZE = 1024 * 1024
        print('[NEW CONNECTION] {} connected.'.format(self.client_address))
        client = self.client_address
    
        try:
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
            # file_size = file_obj['size']
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
            scale_method = file_obj['scale']
            print(f'[SAVING] Saving file locally')
            os.makedirs('./rec_files/', exist_ok=True)
            with open('./rec_files/' + filename, 'wb') as f:
                f.write(file_data)
            print(f'[SAVED] File saved as {filename}')
            self.request.close()

            print(f'[PROCESSING] Sending to queue')
            queue.put_nowait((filename, scale_method))
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"[ERROR] Error de conexión con el cliente {client}: {e}")

        except Exception as e:
            print(f"[ERROR] Error en el manejador de la conexión con el cliente {client}: {e}")


def process_queue():
    try:
        while True:
            while not queue.empty():
                filename, scale_method = queue.get_nowait()
                filetype, encoding = mimetypes.guess_type(filename)
                print(f'[PROCESSING] Processing file {filename}...')
                print(f"[TESTING] Scale method set to {scale_method} with type {type(scale_method)}")
                if filetype.startswith('video/'):
                    # Se genera un proceso hijo para procesar el video
                    p_image = multiprocessing.Process(
                        target=scale_video, args=(filename, 2))
                    print(f'[PROCESSING] Generating son process for {filename}')
                    p_image.start()
                    p_image.join()
                else:
                    # Se genera un proceso hijo para procesar la imagen
                    if scale_method == 0:
                        #Procesar imagen con Interpolado de pixeles
                        p_image = multiprocessing.Process(
                            target=scale_image, args=(filename, 2))
                        print(f'[PROCESSING] Generating son process for {filename}')
                        p_image.start()
                        p_image.join()
                    elif scale_method == 1:
                        # Procesar imagen con AI
                        p_image = multiprocessing.Process(
                            target=scale_image_ia, args=(filename,))
                        print(f'[PROCESSING] Generating son process for {filename}')
                        p_image.start()
                        p_image.join()
                print(f'[PROCESSING] File {filename} processed')
                file_path = f'./upscaled_files/upscaled_{filename}'
                chat_id = int((filename.split("_"))[0])
                print(f'[SENDING] Sending file {filename} to Telegram user')
                os.remove(f'./rec_files/{filename}')
                try:
                    send_file(file_path, filetype, chat_id)
                    os.remove(file_path)
                except FileNotFoundError:
                    print("[ERROR] File not found")
                    send_message(chat_id, "There was an error processing the file.")
    except KeyboardInterrupt:
        print('[TERMINATED] Queue process terminated')
    except ConnectionResetError or BrokenPipeError as e:
        sys.exit(0)

def server(args):

    HOST, PORT = args.ip, args.port

    with open('./data/ipv4.txt', 'r') as f:
        ipv4 = str(f.read())
    with open('./data/ipv6.txt', 'r') as f:
        ipv6 = str(f.read())

    if re.search(ipv6, args.ip):
        try:
            with ForkedTCPServer6((HOST, PORT), TCPRequestHandler) as server:
                print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')
                server.serve_forever()
        except OSError as e:
            print(f'[ERROR] {e} for IP address')
            sys.exit(0)
    elif re.search(ipv4, args.ip):
        try:
            with ForkedTCPServer4((HOST, PORT), TCPRequestHandler) as server:
                print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')

                server.serve_forever()
        except OSError as e:
            print(f'[ERROR] {e} for IP address') 
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', type=str, default='127.0.0.1',
                        help='IP of the server process')
    parser.add_argument('-port', '-p', type=int, default=5556,
                        help='Port of the server process')
    args = parser.parse_args()

    # IPs conecction test: 127.0.0.1, ::1, 172.31.161.195 o fe80::215:5dff:fe7c:b97b

    #! Mejorar manejo de errores

    # Procesa la cola en un proceso hijo

    try:
        queue_process = multiprocessing.Process(target=process_queue)
        queue_process.start()
        print(f'[PROCESSING] Started queue process {queue_process.pid}...')

        # Inicia el servidor y se queda esperando conexiones en el proceso padre
        print(f'[PROCESSING] Started server process')

        try:
            server(args)
        except UnboundLocalError as e:
            print(f'[ERROR] {e}. Server shutting down')
            sys.exit(0)

        # Espera a que los procesos hijos terminen
        queue_process.join()
    except KeyboardInterrupt:
        print('[TERMINATED] Server shutting down')

    print('[PROCESSING] All processes finished.')
