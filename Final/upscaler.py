from multiprocessing import Manager
import os
from queue import Queue
import cv2
from tqdm import tqdm
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.editor as mp
from ffprobe import FFProbe
import ffmpeg
import io
import os
import PIL
import requests
from PIL import Image
import replicate
from telegram_sender import send_message, send_file

# Modulo destinado a escalar imagenes y video por interpolado de pixeles o mediante IA con ESRGAN

# Establecer el API token como una variable de entorno
with open('./data/REPLICATE_KEY.txt', 'r') as f:
    token = str(f.read())
os.environ["REPLICATE_API_TOKEN"] = token

def scale_image(filename, scale):
    # Se especifica el path de la imagen recibida y se convierte a color
    image_path = f'./rec_files/{filename}'
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # Leer la resolución de entrada de la imagen
    alto, ancho = image.shape[:2]
    # Duplicar la resolución de la imagen
    nuevo_alto = alto * scale
    nuevo_ancho = ancho * scale

    # Escalar la imagen con el método cv2.INTER_LANCZOS
    print(f"[SCALING] {filename} scaling with lanczos")
    chat_id = int((filename.split("_"))[0])
    # Se envia mensaje de inicio de escalado y se escala
    send_message(chat_id, "Scaling Image...")
    imagen_escalada = cv2.resize(image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
    print(f"[SCALING] {filename} scaling finished")

    # Exportar la imagen escalada localmente
    print(f"[SCALING] {filename} exporting")
    os.makedirs('./upscaled_files/', exist_ok=True)
    export_path = f'./upscaled_files/upscaled_{filename}'
    cv2.imwrite(export_path, imagen_escalada)
    print(f"[SCALING] {filename} exported succesfully")

    # Informacion de log
    print(f'Resolucion de entrada: {alto}x{ancho}')
    print(f'Razon de escala: x{scale}')
    print(f'Resolucion de salida: {nuevo_alto}x{nuevo_ancho}')
    send_message(chat_id, f"Scaling finished, output resolution: {nuevo_ancho}x{nuevo_alto}")

    # Algoritmo de compresion para lograr que pese menos de 50 MB
    max_size = 50 * 1024 * 1024
    while os.path.getsize(export_path) > max_size:
        compress_image(export_path)

    cv2.waitKey(1000)
    cv2.destroyAllWindows()

def scale_image_ia(filename):
    try:
        # Cargar la imagen de entrada
        image_path = f'./rec_files/{filename}'
        input_image = PIL.Image.open(image_path)
        
        input_file = io.BytesIO()
        input_image.save(input_file, format="JPEG")

        # Ejecutar el modelo de escalado
        output_image = replicate.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
            input={"image": input_file}
        )

        # Descargar la imagen desde la URL
        response = requests.get(output_image)
        output_image = PIL.Image.open(io.BytesIO(response.content))

        # Guardar la imagen de salida
        output_image.save(f"./upscaled_files/upscaled_{filename}")
    except replicate.exceptions.ModelError:
        print("[ERROR] API Out of memory")

def scale_video(filename, scale):
    # Abrir el video original
    video_path = f'./rec_files/{filename}'
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
    # ? Solucion a cv2 no localizando el codec h264 -> Instalar opencv desde sudo apt-get, luego hacer sudo apt-get update y upgrade
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

    # Log de salida
    print(f'Resolucion de entrada: {ancho}x{alto}')
    print(f'Razon de escala: x{escala}')
    print(f'Resolucion de salida: {nuevo_ancho}x{nuevo_alto}')
    send_message(
        chat_id, f"Scaling finished, output resolution: {nuevo_ancho}x{nuevo_alto}")

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    export_path = f"./upscaled_files/upscaled_{filename}"
    max_size = 50 * 1024 * 1024

    if os.path.getsize(export_path) > max_size:
        compress_video(filename, export_path, max_size)

# Algoritmos de compresion para lograr que los archivos pesen menos de 50 MB

def compress_video(filename, export_path, max_size):
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
    print(
        f'[COMPRESSION] Writing finalized: ({os.path.getsize(export_path) // (1024 * 1024)}MB)')

    # Compresion mas agresiva en caso de que siga pesando mas de 50 MB
    if os.path.getsize(export_path) > max_size:
        print(
            f'[COMPRESSION] File is still larger than 50MB ({os.path.getsize(export_path) // (1024 * 1024)}MB), starting agresive compression')
        # Cargar archivo
        clip = VideoFileClip(export_path)

        # Establecer la tasa de bits objetivo
        new_bitrate = f"{int((50 * 8 * 1000) / clip.duration)}k"

        # Compresion a nueva tasa de bits
        print(f'[COMPRESSION] Compressing file')
        clip.write_videofile(export_path, bitrate=new_bitrate)

def compress_image(export_path):
    print(f"[COMPRESSION] The file is too large {os.path.getsize(export_path)}")
    img = Image.open(export_path)
    img.save(export_path, "JPEG", quality=90, optimize=True)