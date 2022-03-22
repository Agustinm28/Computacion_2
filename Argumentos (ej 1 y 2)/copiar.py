import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--copiar", help='archivo origen')
parser.add_argument("-o", "--pegar", help='archivo destino')
args = parser.parse_args()

def copiar():
    with open(args.copiar, 'r+') as f1:
        with open(args.pegar, 'w+') as f2:
            for i in f1:
                f2.write(i)

copiar()