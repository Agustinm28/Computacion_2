import argparse
import sys
import os
import time
import datetime
from os import fork
import subprocess as s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--numprocess', type=int,
                        help='Indica la cantidad de procesos hijos a generar')
    parser.add_argument('-r', '--repetitions', type=int,
                        help='Cantidad de veces a repetir la letra')
    parser.add_argument(
        '-f', '--path', help='Path en el que quiere almacenarse el archivo')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='modo verbose, muestra un mensaje de inicio y finalizacion de cada proceso hijo con su PID')
    args = parser.parse_args()

    w_letters(args)


def w_letters(args):
    dic = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    with open(args.path, 'w+') as file:
        for i in range(args.numprocess):
            for j in range(args.repetitions):
                letter = dic[j % len(dic)]
                if fork() == 0:
                    if args.verbose:
                        print('Writing letter {}, Process {}'.format(
                            letter, os.getpid()))
                    file.write(letter)
                    file.flush()
                    time.sleep(1)
                    sys.exit()
                else:
                    os.wait()
        file.seek(0)
        print(file.read())


if __name__ == '__main__':
    main()
