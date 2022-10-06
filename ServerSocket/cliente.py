import socket
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', required=True, help='direccion IP del servidor')
    parser.add_argument('-p', '--port', required=True, help='puerto del servidor')
    args = parser.parse_args()

    socket_client(args)


def socket_client(args):
    FORMAT = 'utf-8'
    HEADER = 64
    HOST, PORT = args.ip, int(args.port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.connect((HOST, PORT))
        print(f"[CONNECT] Conexion establecida con {HOST} en el puerto {PORT}")

        while True:
            command = input(f'{HOST}> ')

            message = command.encode(FORMAT)
            msg_len = len(message)
            send_len = str(msg_len).encode(FORMAT)
            send_len += b' ' * (HEADER - len(send_len))
            sock.send(send_len) 
            sock.send(message) 
            print(sock.recv(2048).decode(FORMAT)) 


if __name__ == '__main__':
    main()
