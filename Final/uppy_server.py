import socket
import socketserver
import argparse
from multiprocessing import Manager
import pickle
import os
from queue import Queue
import cv2
import requests
from tqdm import tqdm
import multiprocessing
import mimetypes
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.editor as mp
from ffprobe import FFProbe
import ffmpeg

# * UPSCALER

def scale_image(filename, scale):
    print(f"[SCALING] {filename} enter process")
    image_path = f'./rec_files/{filename}'
    print(f"[SCALING] {filename} reading in color")
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # Leer la resolución de entrada de la imagen
    alto, ancho = image.shape[:2]
    # Duplicar la resolución de la imagen
    nuevo_alto = alto * scale
    nuevo_ancho = ancho * scale
    # Escalar la imagen con el método cv2.INTER_LANCZOS
    print(f"[SCALING] {filename} scaling with lanczos")
    chat_id = int((filename.split("_"))[0])
    send_message(chat_id, "Scaling Image...")
    imagen_escalada = cv2.resize(
        image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
    print(f"[SCALING] {filename} finish scaling")
    # Exportar la imagen escalada a un archivo
    print(f"[SCALING] {filename} exporting")
    os.makedirs('./upscaled_files/', exist_ok=True)
    export_path = f'./upscaled_files/upscaled_{filename}'
    print(f"[SCALING] {filename} writing locally")
    cv2.imwrite(export_path, imagen_escalada)
    print(f"[SCALING] {filename} exported succesfully")

    # Informacion de log
    print(f'Resolucion de entrada: {alto}x{ancho}')
    print(f'Razon de escala: x{scale}')
    print(f'Resolucion de salida: {nuevo_alto}x{nuevo_ancho}')

    send_message(chat_id, f"Scaling finished, output resolution: {nuevo_ancho}x{nuevo_alto}")

    # Algoritmo de compresion para lograr que pese menos de 20 MB
    max_size = 20 * 1024 * 1024
    while os.path.getsize(export_path) > max_size:
        print(
            f"[COMPRESSION] The file is too large {os.path.getsize(export_path)}")
        img = Image.open(export_path)
        img.save(export_path, "JPEG", quality=90, optimize=True)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def scale_video(filename, scale):
    video_path = f'./rec_files/{filename}'
    # Abrir el video original
    cap = cv2.VideoCapture(video_path)

    # Obtener el ancho y el alto del video
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Obtener la cantidad de fotogramas del video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=frames, desc="Processing Video",
                unit="frame", colour="green")

    # Definir el factor de escala
    escala = scale

    # Definir el nuevo ancho y alto
    nuevo_ancho = ancho * escala
    nuevo_alto = alto * escala

    # Definir el codec y el nombre del nuevo video
    # ? Solucion a cv2 no localizando el codec h264 -> Instalar opencv desde sudo apt-get, luego hacer sudo apt-get update y uprgrade
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # Codec H264 (avc1), H265 (hvc1)
    os.makedirs('./upscaled_files/', exist_ok=True)
    out = cv2.VideoWriter(
        f"./upscaled_files/upscaled_{filename}", fourcc, 30.0, (nuevo_ancho, nuevo_alto))

    # Leer cada frame del video original y escalarlo
    chat_id = int((filename.split("_"))[0])
    send_message(chat_id, "Scaling Video...")
    while True:
        ret, frame = cap.read()
        if ret:
            pbar.update(1)
            # Escalar el frame con interpolación lanczos
            frame_escalado = cv2.resize(
                frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
            # Escribir el frame escalado en el nuevo video
            out.write(frame_escalado)
        else:
            break

    pbar.close()

    print(f'Resolucion de entrada: {ancho}x{alto}')
    print(f'Razon de escala: x{escala}')
    print(f'Resolucion de salida: {nuevo_ancho}x{nuevo_alto}')
    send_message(chat_id, f"Scaling finished, output resolution: {nuevo_ancho}x{nuevo_alto}")

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Algoritmo de compresion para lograr que pese menos de 50 MB
    export_path = f"./upscaled_files/upscaled_{filename}"
    max_size = 50 * 1024 * 1024
    
    if os.path.getsize(export_path) > max_size:
        print(f'[COMPRESSION] File is larger than 50MB ({os.path.getsize(export_path) // (1024 * 1024)}MB), starting compression')

        # Compresion inicial con H265 codec
        print(f'[COMPRESSION] Writing with H265 codec, this may take a while...')

        # Crear un objeto FFmpeg para el archivo de entrada
        input_stream = ffmpeg.input(export_path)

        # Configurar el códec H.265 para el archivo de salida
        output = f"./upscaled_files/c_upscaled_{filename}"
        output_stream = ffmpeg.output(input_stream, output, vcodec='libx265')

        # Agregar el argumento "-hide_banner" para evitar que FFmpeg imprima información en pantalla
        output_stream = output_stream.global_args('-hide_banner')

        # Agregar el argumento "-loglevel" para mostrar la menor cantidad de información posible
        output_stream = output_stream.global_args('-loglevel', 'quiet')

        # Ejecutar el proceso de codificación
        ffmpeg.run(output_stream)
        os.remove(export_path)
        os.rename(output, export_path)
        print(f'[COMPRESSION] Writing finalized: ({os.path.getsize(export_path) // (1024 * 1024)}MB)')

        # Compresion mas agresiva en caso de que siga pesando mas de 50 MB
        if os.path.getsize(export_path) > max_size:
            print(f'[COMPRESSION] File is still larger than 50MB ({os.path.getsize(export_path) // (1024 * 1024)}MB), starting agresive compression')
            # Cargar archivo
            clip = VideoFileClip(export_path)

            # Establecer la tasa de bits objetivo
            new_bitrate = f"{int((50 * 8 * 1000) / clip.duration)}k"

            # Compresion a nueva tasa de bits
            print(f'[COMPRESSION] Compressing file')
            clip.write_videofile(export_path, bitrate=new_bitrate)

# * SERVER

manager = Manager()  # Creamos una cola compartida para comunicarse con los procesos hijos
queue = manager.Queue()

with open('./data/BOT_CREDENTIALS.txt', 'r') as f:
    token = str(f.read())


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

# Enviar video al usuario de telegram
def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)

def send_file(file_path, filetype, chat_id):
    if filetype.startswith('video/'):
        send_message(chat_id, "Upscaled video:")
        url = f"https://api.telegram.org/bot{token}/sendVideo"
        files = {"video": open(file_path, "rb")}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    else:
        send_message(chat_id, "Upscaled Image:")
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": open(file_path, "rb")}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    print(f'[SENDING] File sended')


def process_queue():
    while True:
        while not queue.empty():
            filename = queue.get_nowait()
            filetype, encoding = mimetypes.guess_type(filename)
            print(f'[PROCESSING] Processing file {filename}...')
            if filetype.startswith('video/'):
                # Procesado de Video
                scale_video(filename, 2)
            else:
                # Procesado de imagen
                scale_image(filename, 2)
            print(f'[PROCESSING] File {filename} processed')
            file_path = f'./upscaled_files/upscaled_{filename}'
            chat_id = int((filename.split("_"))[0])
            print(f'[SENDING] Sending file {filename} to Telegram user')
            send_file(file_path, filetype, chat_id)
            os.remove(f'./rec_files/{filename}')
            os.remove(file_path)


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
