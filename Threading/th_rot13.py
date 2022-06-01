import multiprocessing as mp
from multiprocessing import Pipe, Queue
import threading as th
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

    t1 = th.Thread(target=readInput, name='t1', args=(q, r))
    t2 = th.Thread(target=R13_e, name='t2', args=(q, e))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
