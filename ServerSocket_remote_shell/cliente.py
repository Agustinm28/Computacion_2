import socket
import argparse
import pickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', required=True, help='direccion IP del servidor')
    parser.add_argument('-p', '--port', required=True,
                        help='puerto del servidor')
    args = parser.parse_args()

    socket_client(args)


def socket_client(args):
    HOST, PORT = args.ip, int(args.port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.connect((HOST, PORT))
        print(f"Conexion establecida con {HOST} en el puerto {PORT}")

        while True:
            command = input('> ')
            sock.sendall(pickle.dumps(f'{command}\n'))

            if command == 'exit':
                break

            out = ''

            while True:
                packet = pickle.loads(sock.recv(4096))

                out += packet

                if (packet[-3::] == 'EOF'):
                    out = out[:-3:]
                    break

                elif packet[:5:] == 'ERROR':
                    break

                out += '\n' if out[-1::] != '\n' else ''

            print(f'\n{out}')

        goodbye = pickle.loads(sock.recv(4096))
        print(f'\n{goodbye}')


if __name__ == '__main__':
    main()
