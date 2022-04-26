import argparse
import os
import sys
import time
import mmap
import signal
from os import fork


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='Path del archivo')
    args = parser.parse_args()

    mapp(args)


def store_up(segment):
    leido = (segment.read(1024))
    segment.seek(0)
    segment.write(leido.decode().upper().encode())
    os.kill(os.fork(), signal.SIGUSR1)


def mapp(args):

    with open('file.txt', 'w+') as file:
        segment = mmap.mmap(file.fileno(), 1024)
        signal.signal(signal.SIGUSR1, store_up(segment))
        ppid = []

        for i in range(2):
            if fork() == 0:
                ppid.append(os.getpid())
            else:
                print(segment.readline())
                os.wait()
        for line in sys.stdin:
            if os.getpid() == ppid[0]:
                segment.write(bytes(line))
                signal.raise_signal(signal.SIGUSR1)
                segment.seek()
                signal.pause()
                exit()


if __name__ == '__main__':
    main()
