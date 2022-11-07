import math
from celery import Celery
import argparse
import numpy as np
import os, time

app = Celery('tasks', broker='redis://localhost', backend='redis://localhost:6379')

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", required=True, help="Path del archivo")
    parser.add_argument("-c", required=True, help="Funcion de calculo", choices=["pot", "raiz", "log"])
    return parser.parse_args()

def open_file(path):
    with open(path) as f:
        entryMatrix = f.read()
    return entryMatrix

@app.task
def raiz(entryMatrix):
    exitMatrix = []
    for row in entryMatrix:
        if isinstance(row, list):
            for col in row:
                print(col)
                value = math.sqrt(int(col))
                exitMatrix.append(value)
        else:
            pass
    return exitMatrix

@app.task
def pot(entryMatrix):
    exitMatrix = []
    for row in entryMatrix:
        if isinstance(row, list):
            for col in row:
                print(col)
                value = int(col)*int(col)
                exitMatrix.append(value)
        else:
            pass
    return exitMatrix 

@app.task
def log(entryMatrix):
    exitMatrix = []
    for row in entryMatrix:
        if isinstance(row, list):
            for col in row:
                print(col)
                value = math.log(int(col))
                exitMatrix.append(value)
        else:
            pass
    return exitMatrix

def calculo(c, Matrix):
    if c == 'raiz':
        return raiz.delay(Matrix)
    elif c == 'pot':
        return pot.delay(Matrix)
    elif c == 'log':
        return log.delay(Matrix)

def print_matrix(entryMatrix, exitMatrix):

    rows_n = len(entryMatrix)
    cols_n = len(entryMatrix[0])

    exitMatrix = np.array(exitMatrix).reshape(rows_n, cols_n)
    print(exitMatrix)

def main(args):
    fileMatrix = open_file(args.f)

    entryMatrix = []
    row = []
    for w in fileMatrix:
        if w == '\n':
            entryMatrix.append(row)
            row = []
        elif w == ' ' or w == ',':
            pass
        else:
            row.append(int(w))
    entryMatrix.append(row) 

    exitMatrix = calculo(args.c, entryMatrix)

    rows_n = len(entryMatrix)
    cols_n = len(entryMatrix[0])

    print('Matriz de entrada: \n')
    entryMatrix = np.array(entryMatrix).reshape(rows_n, cols_n)
    print(entryMatrix)

    print(f'\nMatriz de salida con {args.c}: \n')
    print_matrix(entryMatrix, exitMatrix.get())

if __name__ == '__main__':
    main(args())