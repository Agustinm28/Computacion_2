from datetime import date
import cv2
import numpy as np
import telegram_bot as tb

def main():
    today = date.today()
    generate_log(today)
    # Captura el video a ser analizado
    cap = cv2.VideoCapture('./assets/airport_sd.mp4')
    # Determina el algoritmo de sustraccion a utilizar, MOG2 en este caso
    fgbg = cv2.createBackgroundSubtractorMOG2()
    # Se utilizara posteriormente para mejorar imagen binaria
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

    while True:

        ret, frame = cap.read()
        if ret == False: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Se dibuja un rectangulo en frame, para señalar el estado del area en analisis (mov o no)
        cv2.rectangle(frame,(0,0),(frame.shape[1],40),(0,0,0),-1)
        color = (0, 255, 0)
        state_text = "Status: no movement detected"

        #Se especifican los puntos extremos del area a analizar, ordenados de forma horaria
        area_pts = np.array([[200,320], # esquina inferior izq (x,y)
        [480,320], # esquina inferior der
        [620,frame.shape[0]], # punto medio superior
        [50,frame.shape[0]]]) # punto medio superior izquierdo

        # Con ayuda de una imagen auxiliar, determinamos el area sobre la cual actuara el detector de movimiento
        imAux = np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
        imAux = cv2.drawContours(imAux, [area_pts], -1, (255), -1)
        image_area = cv2.bitwise_and(gray, gray, mask=imAux)

        # Se obtiene la imagen binaria donde la región en blanco representa la existencia de movimiento
        fgmask = fgbg.apply(image_area)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        fgmask = cv2.dilate(fgmask, None, iterations=2)

        # Encontramos los contornos presentes en fgmask, para luego basándonos en su área poder determina si existe movimiento
        cnts = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for cnt in cnts:
            # Cuando un contorno tenga un área mayor a 500, se dibujará un recuadro delimitador que rodeará al área blanca en movimiento
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x,y), (x+w, y+h),(0,255,0), 2)
                # Obtener el tiempo de reproducción actual en milisegundos
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC)
                # Convertir el tiempo actual a minutos
                current_time_secs = int(current_time/1000)
                current_time_min = int(current_time/60000)
                state_text = f"Status: Movement Detected! Time: {current_time_min}:{current_time_secs}"
                add_log(state_text)
                color = (0, 0, 255)    

        # Visuzalizamos el alrededor del área que vamos a analizar y el estado de la detección de movimiento        
        cv2.drawContours(frame, [area_pts], -1, color, 2)
        cv2.putText(frame, state_text , (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color,2)

        cv2.imshow('fgmask', fgmask)
        cv2.imshow("frame", frame)

        k = cv2.waitKey(70) & 0xFF
        if k == 27:
            break
    
    send_log()
    cap.release()
    cv2.destroyAllWindows()

def generate_log(today):
    with open('./data/motion_log.txt', 'w') as f:
        f.write(f"[ MOTION DETECTION REPORT - {str(today)} ]")

def add_log(status):
    with open('./data/motion_log.txt') as f:
        review = f.read()
    with open('./data/motion_log.txt', 'a') as f:
        if status not in review:
            f.write('\n')
            f.write(str(status))
        else:
            pass
    
def send_log():
    with open('./data/motion_log.txt') as f:
        report_data = f.read()
        tb.send_message(report_data)


if __name__ == '__main__':
    main()