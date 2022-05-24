'''
Realizar un programa en python que reciba por argumentos:

-p cantidad_procesos

-f /ruta/al/archivo_matriz.txt

-c funcion_calculo
El programa deberá leer una matriz almacenada en el archivo de texto pasado por argumento -f, y deberá calcular la funcion_calculo para cada uno de sus elementos.

Para aumentar la performance, el programa utilizará un Pool de procesos, y cada proceso del pool realizará los cálculos sobre una de las filas de la matriz.

La funcion_calculo podrá ser una de las siguientes:

raiz: calcula la raíz cuadrada del elemento.
pot: calcula la potencia del elemento elevado a si mismo.
log: calcula el logaritmo decimal de cada elemento.

-----------------------------------------------------------------------------------------------------------------------------------
Ejemplo de uso:
Suponiendo que el archivo /tmp/matriz.txt tenga este contenido:

1, 2, 3
4, 5, 6
python3 calculo_matriz -f /tmp/matriz.txt -p 4 -c pot
1, 4, 9
16, 25, 36
-----------------------------------------------------------------------------------------------------------------------------------
'''
import multiprocessing as mp
from multiprocessing import Value, Array, Pool
import argparse
import math
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--process', help='Cantidad de procesos')
    parser.add_argument(
        '-f', '--path', help='Path en el que quiere almacenarse el archivo')
    parser.add_argument('-c', '--calc',
                        choices=['raiz', 'pot', 'log'], help='Funcion de calculo')
    args = parser.parse_args()

    readInput(args)


def raiz(num):
    return round(math.sqrt(int(num)))


def pot(num):
    return round(math.pow(int(num), 2))


def log(num):
    return round(math.log10(int(num)))


def readInput(args):

    matriz = []
    with open(args.path, 'r') as file:
        for line in file.readlines():
            row = line.strip("\n ").split(',')
            matriz.append(row)
    try:
        len(matriz) < int(args.process)
    except:
        for j in range(int(args.process) - len(matriz)):
            matriz.append([])
    calculation(args, matriz)


def calculation(args, matriz):
    with Pool(int(args.process)) as p:
        for i in range(len(matriz)):
            function = {'raiz': raiz, 'pot': pot, 'log': log}[args.calc]
            matriz[i] = p.map(function, matriz[i])

    for row in matriz:
        print(', '.join(str(elem) for elem in row))


if __name__ == '__main__':
    main()
