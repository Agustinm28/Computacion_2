import argparse, sys, datetime, os, time
from os import fork

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--number', type=int, help='numero de procesos hijos a ejecutar')
    parser.add_argument('-v','--verbose', action='store_true', help='modo verbose, muestra un mensaje de inicio y finalizacion para cada proceso hijo')
    args = parser.parse_args()

    sum_par(args)

def sum_par(args):
    for i in range(args.number):
        suma = 0
        if fork() == 0:
            if args.verbose:
                print('Starting process {}'.format(os.getpid()))
            for j in range(0, os.getpid(), 2):
                suma += j
            if args.verbose:
                print('Ending process {}'.format(os.getpid()))
            print('{} - {}: {}'.format(os.getpid(), os.getppid(), suma))
            sys.exit()
        else:
            os.wait()

if __name__ == '__main__':
    main()