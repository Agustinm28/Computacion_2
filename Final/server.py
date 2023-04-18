from asyncio import subprocess
import asyncio
import socketserver as ss
import argparse
import pickle as p
from subprocess import Popen, PIPE
import subprocess


async def handle(reader, writer):

    FORMAT = 'utf-8' # Se define el formato de codificacion
    HEADER = 64 # Tamaño de bytes del encabezado inicial
    DISCONNECT_MESSAGE = '!DISCONNECT'
    print('[NEW CONNECTION] {} connected.'.format(writer.get_extra_info('peername')))

    # Se reciben los datos del cliente
    while True:
        # Se recibe el encabezado y decodifica
        msg_len = (await reader.read(HEADER)).decode(FORMAT)
        # Si el encabezado no esta vacio
        if msg_len:
            msg_len = int(msg_len)
            # Recibir el mensaje con la longitud indicada por el encabezado y decodificarlo usando el formato especificado
            command = (await reader.read(msg_len)).decode(FORMAT)
            if command == DISCONNECT_MESSAGE or command == 'exit':
                print(DISCONNECT_MESSAGE)
                break
            
            print('[{}] > Command {} Executed'.format(writer.get_extra_info('peername'), command))
            output = 'output: \n'
            # obtener la salida del comando como una cadena de texto usando la función subprocess.getoutput()
            output += subprocess.getoutput(command)
            # enviar la cadena codificada al cliente usando el formato especificado
            writer.write(output.encode(FORMAT))
            await writer.drain()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True, type=int, default=0, help='puerto del servidor')
    args = parser.parse_args()

    await server(args)


async def server(args):

    HOST, PORT = '127.0.0.1', args.port

    async with await asyncio.start_server(handle, HOST, PORT) as server:
        print(f'[WAITING] Server is waiting for connections on {HOST}:{PORT}')
        print(f'[TASK] {asyncio.current_task().get_name()}')

        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
