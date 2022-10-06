import socket
import argparse
import re

ipv4 = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'''

ipv6 = '''(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|
        ([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:)
        {1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1
        ,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}
        :){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{
        1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA
        -F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a
        -fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0
        -9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,
        4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}
        :){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9
        ])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0
        -9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]
        |1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]
        |1{0,1}[0-9]){0,1}[0-9]))'''

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

    if re.search(ipv6, args.ip):
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:

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
        
    if re.search(ipv4, args.ip):
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
