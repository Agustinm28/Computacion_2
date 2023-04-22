import socketserver
import argparse
from multiprocessing import Manager
import pickle
import os
from queue import Queue
import subprocess
import time
import cv2
from tqdm import tqdm
import multiprocessing
import mimetypes
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

#* UPSCALER

def scale_image(filename, scale):
    image_path = f'./rec_files/{filename}'
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # Leer la resolución de entrada de la imagen
    alto, ancho = image.shape[:2]
    # Duplicar la resolución de la imagen
    nuevo_alto = alto * scale
    nuevo_ancho = ancho * scale
    # Informacion de log
    print(f'Resolucion de entrada: {alto}x{ancho}')
    print(f'Razon de escala: x{scale}')
    print(f'Resolucion de salida: {nuevo_alto}x{nuevo_ancho}')
    # Escalar la imagen con el método cv2.INTER_LANCZOS
    imagen_escalada = cv2.resize(image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Exportar la imagen escalada a un archivo
    os.makedirs('./upscaled_files/', exist_ok=True)
    export_path = f'./upscaled_files/upscaled_{filename}'
    cv2.imwrite(export_path, imagen_escalada)

    # Algoritmo de compresion para lograr que pese menos de 50 MB
    max_size = 20 * 1024 * 1024
    while os.path.getsize(export_path) > max_size:
        print(f"[COMPRESSION] The file is too large {os.path.getsize(export_path)}")
        img = Image.open(export_path)
        img.save(export_path, "JPEG", quality=90, optimize=True)

def scale_video(filename, scale):
    video_path = f'./rec_files/{filename}'
    # Abrir el video original
    cap = cv2.VideoCapture(video_path)

    # Obtener el ancho y el alto del video
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Obtener la cantidad de fotogramas del video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=frames, desc="Processing Video", unit="frame", colour="green")

    # Definir el factor de escala
    escala = scale

    # Definir el nuevo ancho y alto
    nuevo_ancho = ancho * escala
    nuevo_alto = alto * escala

    # Definir el codec y el nombre del nuevo video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v") # Codec H265
    os.makedirs('./upscaled_files/', exist_ok=True)
    out = cv2.VideoWriter(f"./upscaled_files/upscaled_{filename}", fourcc, 30.0, (nuevo_ancho, nuevo_alto))

    # Leer cada frame del video original y escalarlo
    while True:
        ret, frame = cap.read()
        if ret:
            pbar.update(1)
            # Escalar el frame con interpolación lanczos
            frame_escalado = cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
            # Escribir el frame escalado en el nuevo video
            out.write(frame_escalado)
        else:
            break

    pbar.close()

    # Algoritmo de compresion para lograr que pese menos de 50 MB
    export_path = f"./upscaled_files/upscaled_{filename}"
    max_size = 20 * 1024 * 1024
    print('File_Size: ' + str(os.path.getsize(export_path)/1024/1024))

    #! NO FUNCIONA
    if os.path.getsize(export_path) > max_size:
        # Cargar el video en Moviepy
        video = VideoFileClip(export_path)

        # Obtener el tamaño total del archivo de video
        video_size = video.size

        # Calcular el número de partes necesarias
        num_parts = (video_size // max_size) + 1

        # Calcular la duración de cada parte
        part_duration = video.duration / num_parts

        # Utilizar la función subclip() de Moviepy para dividir el archivo en partes
        for i in range(num_parts):
            start_time = i * part_duration
            end_time = (i+1) * part_duration if i != num_parts-1 else video.duration
            output_path = f"./divided_files/{filename}_{i}.mp4"
            video.subclip(start_time, end_time).write_videofile(output_path, codec="libx264")

    print(f'Resolucion de entrada: {ancho}x{alto}')
    print(f'Razon de escala: x{escala}')
    print(f'Resolucion de salida: {nuevo_ancho}x{nuevo_alto}')

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()

#* SERVER

manager = Manager()  # Creamos una cola compartida para comunicarse con los procesos hijos
queue = manager.Queue()

class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


class TCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        BUFFER_SIZE = 1024 * 1024
        print('[NEW CONNECTION] {} connected.'.format(self.client_address))

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



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True,
                        type=int, default=0, help='puerto del servidor')
    args = parser.parse_args()

    # Inicia el servidor en un proceso hijo
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

def process_queue():
    while True:
        while not queue.empty():
            filename = queue.get_nowait()
            filetype, encoding = mimetypes.guess_type(filename)
            print(f'[PROCESSING] Processing file {filename}...')
            if filetype.startswith('video/'):
                # Procesado de Video
                scale_video(filename, 2)
                print(f'[PROCESSING] File {filename} processed')
            else:
                # Procesado de imagen
                scale_image(filename, 2)
                print(f'[PROCESSING] File {filename} processed')

def server(args):

    HOST, PORT = '127.0.0.1', args.port

    with ForkedTCPServer((HOST, PORT), TCPRequestHandler) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')

        server.serve_forever()

if __name__ == "__main__":
    main()
