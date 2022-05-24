'''
Escribir un programa que genere dos hijos utilizando multiprocessing.

Uno de los hijos deberá leer desde stdin texto introducido por el usuario, y deberá escribirlo en un pipe (multiprocessing).

El segundo hijo deberá leer desde el pipe el contenido de texto, lo encriptará utilizando el algoritmo ROT13, y lo almacenará en una cola de mensajes (multiprocessing).

El primer hijo deberá leer desde dicha cola de mensajes y mostrar el contenido cifrado por pantalla.
'''
import multiprocessing as mp
from multiprocessing import Pipe, Queue
import os
import sys
import time


def readInput(q, r_pipe):
    sys.stdin = open(0)
    print('Ingrese una cadena: ')
    for line in sys.stdin:
        r_pipe.send(line)
        try:
            print('Cadena codificada: %s' % q.get())
        except:
            print('Cola vacia... saliendo')
            break
        print('Ingrese una cadena: ')
    r_pipe.close()


def R13_e(q, e_pipe):
    while True:
        etxt = e_pipe.recv()
        abc = 'abcdefghijklmnopqrstuvwxyz'
        convert = ''.join([abc[(abc.find(c)+13) % 26] for c in etxt])
        q.put(convert)


if __name__ == '__main__':
    e, r = mp.Pipe()
    q = mp.Queue()

    p1 = mp.Process(target=readInput, args=(q, r))
    p2 = mp.Process(target=R13_e, args=(q, e))

    p1.start()
    p2.start()
    p1.join()
    p2.join()
