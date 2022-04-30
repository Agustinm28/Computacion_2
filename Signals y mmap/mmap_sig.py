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


def store_up(segment, cpid, args):
    for line in sys.stdin:
        if os.getpid() == cpid[0]:
            print(line)
            if os.getpid() == cpid[0]:
                print('Hijo_1')
                segment.write(bytes(line))
                signal.raise_signal(signal.SIGUSR1)

            elif os.getpid() == cpid[1]:
                print('Hijo_2')
            for h in range(2):
                signal.sigwait([signal.SIGUSR1])

            readLine = segment.readline()

            with open(args.file, 'w') as file:
                file.write(readLine.upper())


def mapp(args):

    with open('file.txt', 'w+') as file:
        segment = mmap.mmap(-1, 1024)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)
        ppid = os.getpid()
        cpid = []

        for i in range(2):
            if os.getpid() == ppid:
                cpid.append(os.fork())
            else:
                os.wait()
        if os.fork():
            w = os.fdopen(w, 'w')
            print(cpid)
            w.write(f'{cpid}')
            w.close()
        else:
            os.close(w)
            r = os.fdopen(r, 'r')
            cpid = r.read()
            print(cpid)
            r.close()

        store_up(segment, cpid, args)


if __name__ == '__main__':
    main()
