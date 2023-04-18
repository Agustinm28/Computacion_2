import cv2
from tqdm import tqdm

def scale_image(image, scale):
    image = image
    # Leer la resolución de entrada de la imagen
    alto, ancho = image.shape[:2]
    print(f'Resolucion de entrada: {alto}x{ancho}')
    # Duplicar la resolución de la imagen
    scale = scale
    nuevo_alto = alto * scale
    nuevo_ancho = ancho * scale
    print(f'Razon de escala: x{scale}')
    print(f'Resolucion de salida: {nuevo_alto}x{nuevo_ancho}')
    # Escalar la imagen con el método cv2.INTER_LANCZOS
    imagen_escalada = cv2.resize(image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LANCZOS4)
    #cv2.imshow("Imagen original", imagen)
    #cv2.imshow("Imagen escalada", imagen_escalada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Exportar la imagen escalada a un archivo
    cv2.imwrite("foto_escalada.jpg", imagen_escalada)

def scale_video():
    # Abrir el video original
    cap = cv2.VideoCapture("./assets/airport_hd.mp4")

    # Obtener el ancho y el alto del video
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Obtener la cantidad de fotogramas del video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=frames, desc="Processing Video", unit="frame", colour="green")

    # Definir el factor de escala
    escala = 4

    # Definir el nuevo ancho y alto
    nuevo_ancho = ancho * escala
    nuevo_alto = alto * escala

    # Definir el codec y el nombre del nuevo video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("./assets/video_escalado.mp4", fourcc, 30.0, (nuevo_ancho, nuevo_alto))

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

    print(f'Resolucion de entrada: {ancho}x{alto}')
    print(f'Razon de escala: x{escala}')
    print(f'Resolucion de salida: {nuevo_ancho}x{nuevo_alto}')

    # Liberar los recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    scale_video()