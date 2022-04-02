import argparse, sys, datetime, subprocess
from subprocess import Popen

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--command', help='comando a ejecutar')
    parser.add_argument('-f','--output_file', help='archivo con salida del comando')
    parser.add_argument('-l','--log_file', help='fecha y hora de la ejecucion del comando')
    args = parser.parse_args()

    files(args)

def files(args):
    with open(args.output_file, 'a') as salida:
        with open(args.log_file, 'a') as log:
            ff = subprocess.Popen(args.command, stdout = salida, stderr=subprocess.PIPE, shell = True)
            print(ff.args, file=salida)
            fl = subprocess.Popen(['echo', '{}: Comando "{}" ejecutado correctamente.'.format(datetime.datetime.now(), args.command)], stdout = log)

if __name__ == '__main__':
    main()