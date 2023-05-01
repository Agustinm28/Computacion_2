import socketserver
import argparse
from multiprocessing import Manager
import pickle
import os
from queue import Queue
from tqdm import tqdm
import multiprocessing
import mimetypes
from telegram_sender import send_file, send_message
from upscaler import scale_image, scale_image_ia, scale_video

# Servidor del bot, encargado de recibir los archivos y procesarlos

manager = Manager()  # Creamos una cola compartida para comunicarse con los procesos hijos
queue = manager.Queue()


class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


class TCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        BUFFER_SIZE = 1024 * 1024
        print('[NEW CONNECTION] {} connected.'.format(self.client_address))
        client = self.client_address

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
        print(f'[SAVING] Saving file locally')
        os.makedirs('./rec_files/', exist_ok=True)
        with open('./rec_files/' + filename, 'wb') as f:
            f.write(file_data)
        print(f'[SAVED] File saved as {filename}')
        self.request.close()

        print(f'[PROCESSING] Sending to queue')
        queue.put_nowait(filename)

def process_queue():
    while True:
        while not queue.empty():
            filename = queue.get_nowait()
            filetype, encoding = mimetypes.guess_type(filename)
            print(f'[PROCESSING] Processing file {filename}...')
            if filetype.startswith('video/'):
                # Procesado de Video
                p_image = multiprocessing.Process(
                    target=scale_video, args=(filename, 2))
                print(f'[PROCESSING] Generating son process for {filename}')
                p_image.start()
                p_image.join()
            else:
                # Procesado de imagen
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
                send_message(chat_id, "There was an error processing the file")

def server(args):

    HOST, PORT = args.ip, args.port

    with ForkedTCPServer((HOST, PORT), TCPRequestHandler) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')

        server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', type=str, default='127.0.0.1',
                        help='IP of the precess server')
    parser.add_argument('-port', '-p', type=int, default=5556,
                        help='Port of the process server')
    args = parser.parse_args()

    # Inicia el servidor en un proceso hijo
    #! Mejorar manejo de errores
    #! Que el proceso padre se quede esperando conexiones, y el hijo procese la queue, tener dos hijos es redundante
    server_process = multiprocessing.Process(target=server, args=(args,))
    server_process.start()
    print(f'[PROCESSING] Started server process {server_process.pid}...')

    # Procesa la cola en otro proceso hijo
    queue_process = multiprocessing.Process(target=process_queue)
    queue_process.start()
    print(f'[PROCESSING] Started queue process {queue_process.pid}...')

    # Espera a que los procesos hijos terminen
    queue_process.join()
    server_process.join()

    print('[PROCESSING] All processes finished.')
