from multiprocessing import Manager
import os
from queue import Queue
import subprocess
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
from compresser import compress_image, compress_video

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
    send_message(chat_id, "Scaling Image (Interpolation)...")
    imagen_escalada = cv2.resize(
        image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
    print(f"[SCALING] {filename} scaling finished")

    # Aplicar filtro de reduccion de ruido bilateral
    print(f"[DENOISING] {filename} denoising image")
    imagen_escalada = cv2.bilateralFilter(imagen_escalada, 7, 50, 50)
    print(f"[DENOISING] {filename} denoising finished")

    # Shapening de bordes con filtro de unsharp mask
    print(f"[SHARPENING] {filename} sharpening image")
    sigma = 1
    amount = 1.5
    threshold = 0
    blurred = cv2.GaussianBlur(imagen_escalada, (0, 0), sigma)
    imagen_escalada = cv2.addWeighted(imagen_escalada, 1 + amount, blurred, -amount, threshold)
    print(f"[SHARPENING] {filename} sharpening finished")

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
        chat_id = int((filename.split("_"))[0])

        input_file = io.BytesIO()
        input_image.save(input_file, format="JPEG")

        # Ejecutar el modelo de escalado
        send_message(chat_id, "Scaling Image (AI)...")
        output_image = replicate.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
            input={"image": input_file, "face_enhance":False}
        )

        # Descargar la imagen desde la URL
        response = requests.get(output_image)
        output_image = PIL.Image.open(io.BytesIO(response.content))
        width, height = output_image.size
        send_message(chat_id, f"Scaling finished, output resolution: {width}x{height}")

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
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # Codec H264 (avc1), H265 (hvc1)
    os.makedirs('./upscaled_files/', exist_ok=True)
    out = cv2.VideoWriter(f"./upscaled_files/upscaled_{filename}", fourcc, 30.0, (nuevo_ancho, nuevo_alto))

    # Obtener chat_id del usuario a partir del filename
    chat_id = int((filename.split("_"))[0])
    send_message(chat_id, "Scaling Video...")

    # Get the output of ffprobe as a string
    output_audio = subprocess.run(["ffprobe", "-show_streams", video_path], capture_output=True, text=True).stdout

    # Usar ffmpeg para extraer el audio del video original
    # Check if the output contains the word "audio"
    if "audio" in output_audio:
        # The video has audio, extract it
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "copy", "audio.aac"])
    else:
        # The video has no audio, do nothing
        print("[PROCESS] The video has no audio")

    # Leer cada frame del video original y escalarlo
    while True:
        ret, frame = cap.read()
        if ret:
            pbar.update(1)
            # Escalar el frame con interpolación lanczos
            frame_escalado = cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
            # Aplicar filtro de reduccion de ruido bilateral
            frame_escalado = cv2.bilateralFilter(frame_escalado, 7, 50, 50)
            # Shapening de bordes con filtro de unsharp mask
            sigma = 1
            amount = 1.5
            threshold = 0
            blurred = cv2.GaussianBlur(frame_escalado, (0, 0), sigma)
            frame_escalado = cv2.addWeighted(frame_escalado, 1 + amount, blurred, -amount, threshold)
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

    export_path = f"./upscaled_files/upscaled_{filename}"
    output = f"./upscaled_files/a_upscaled_{filename}"
    # Usar ffmpeg para aplicar el audio al nuevo video escalado
    # Check if the audio file exists
    if os.path.exists("audio.aac"):
        # The audio file exists, apply it to the new video
        subprocess.run(["ffmpeg", "-v", "quiet", "-stats", "-i", export_path, "-i", "audio.aac", "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-y", output])
        os.remove(export_path)
        os.rename(output, export_path)
    else:
        # The audio file does not exist, do nothing or handle the case
        print("[PROCESS] The audio file does not exist")

    cv2.destroyAllWindows()

    try:
        os.remove("audio.aac")
    except OSError as e:
        print(f"Error: {e.filename} - {e.strerror}.")
    
    # Comprime el video si pesa mas de 50MB
    max_size = 50 * 1024 * 1024
    if os.path.getsize(export_path) > max_size:
        input_path = f"./upscaled_files/upscaled_{filename}"
        output_path = f"./upscaled_files/c_upscaled_{filename}"
        send_message(chat_id, "Compressing video, this may take a while...")
        compress_video(input_path, output_path, 50) 