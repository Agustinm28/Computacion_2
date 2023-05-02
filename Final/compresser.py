import os
import ffmpeg
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

def compress_video(input_path:str, export_path:str, max_size:int):
    print(f'[COMPRESSION] File is larger than {max_size}MB ({os.path.getsize(input_path) // (1024 * 1024)}MB), starting compression')

    # Compresion inicial con H265 codec
    print(f'[COMPRESSION] Writing with H265 codec, this may take a while...')

    # Crear un objeto FFmpeg para el archivo de entrada
    input_stream = ffmpeg.input(input_path)

    # Configurar el códec H.265 para el archivo de salida
    output = export_path
    output_stream = ffmpeg.output(input_stream, output, vcodec='libx265')

    # Agregar el argumento "-loglevel" para mostrar la menor cantidad de información posible
    output_stream = output_stream.global_args('-loglevel', 'quiet')
    output_stream = output_stream.global_args('-stats')

    # Ejecutar el proceso de codificación
    ffmpeg.run(output_stream)

    # Se reemplaza el archivo original por el comprimido
    os.remove(input_path)
    os.rename(export_path, input_path)
    print( f'[COMPRESSION] Writing finalized: ({os.path.getsize(input_path) // (1024 * 1024)}MB)')

    # Compresion mas agresiva en caso de que siga pesando mas de los MB maximos
    if os.path.getsize(input_path) > max_size * 1024 * 1024:
        print(
            f'[COMPRESSION] File is still larger than {max_size}MB ({os.path.getsize(export_path) // (1024 * 1024)}MB), starting agresive compression')
        # Cargar archivo
        clip = VideoFileClip(input_path)

        # Establecer la tasa de bits objetivo
        new_bitrate = f"{int((max_size * 8 * 1000) / clip.duration)}k"

        # Compresion a nueva tasa de bits
        print(f'[COMPRESSION] Compressing file')
        clip.write_videofile(input_path, bitrate=new_bitrate)


def compress_image(export_path):
    print(
        f"[COMPRESSION] The file is too large {os.path.getsize(export_path)}")
    img = Image.open(export_path)
    img.save(export_path, "JPEG", quality=90, optimize=True)
