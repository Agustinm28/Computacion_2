import multiprocessing as mp
import sys


def main():

    q = mp.Queue()
    p_comn, c_comn = mp.Pipe()

    hijo1 = mp.Process(target=readInput, args=(q, c_comn))
    hijo2 = mp.Process(target=rot13, args=(q, p_comn))

    hijo1.start()
    hijo2.start()

    while hijo1.is_alive() or hijo2.is_alive():
        pass


def readInput(queue, pipe):
    sys.stdin = open(0)
    print('Ingrese cadena: ')

    for line in sys.stdin:
        pipe.send(line)
        if line == '\n':
            return
        print(f'Salida codificada: {queue.get()}\n')
        print('Ingrese cadena: ')


def rot13(queue, pipe):
    dic = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    while True:
        enc = pipe.recv()
        if enc != '\n':
            aux = []
            enc = enc.split()

            for e in enc:
                for char in e:
                    if char == '\n':
                        continue
                    elif char.isupper():
                        if char == 'Ñ':
                            aux.append(dic[(dic.index('N') + 13) % 26].lower())
                        else:
                            aux.append(dic[(dic.index(char) + 13) % 26])
                    elif char == 'ñ':
                        aux.append(dic[(dic.index('N') + 13) % 26])
                    else:
                        aux.append(
                            dic[(dic.index(char.upper()) + 13) % 26].lower())
                aux.append(' ')
            enc = ''.join(char for char in aux)
            queue.put(enc)

        else:
            return


if __name__ == '__main__':
    main()
