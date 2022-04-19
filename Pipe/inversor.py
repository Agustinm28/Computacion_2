import argparse
import os
import time
from os import fork
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--path', help='Path en el que quiere almacenarse el archivo')
    args = parser.parse_args()

    invert(args)


def invert(args):
    r, w = os.pipe()

    with open(args.path, 'r+') as f:
        for i in f.readlines():
            line = i.strip()
            if fork() == 0:
                os.close(r)
                w = os.fdopen(w, 'w')
                w.write(f'{line[::-1]}\n')
                w.close()
                sys.exit(0)
            else:
                os.wait()
        f.seek(0)
        os.close(w)
        r = os.fdopen(r, 'r')
        print(r.read())
        r.close()


if __name__ == '__main__':
    main()
