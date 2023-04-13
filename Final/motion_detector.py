import cv2
import numpy as np

# Se captura el video
cap = cv2.VideoCapture('vtest.avi')
# Se llama al algoritmo de sustraccion, en este caso se usara MOG2
fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

while True:

    # Se leen los fotogramas
    ret, frame = cap.read()
    if ret == False: break

    # Se obtiene la mascara del primer plano, donde los objetos en blanco son los objetos en movimiento
    fgmask = fgbg.apply(frame)

    # Se visualizan fgmask y frame, es decir, el frame analizado y su version sustraida (blanco y negro)
    cv2.imshow('fgmask',fgmask)
    cv2.imshow('frame', frame)

    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()