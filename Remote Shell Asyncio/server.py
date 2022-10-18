from asyncio import subprocess
import asyncio
import socketserver as ss
import socket
import argparse
import pickle as p
import sys
import math
from subprocess import Popen, PIPE
import subprocess


async def handle(reader, writer):

    FORMAT = 'utf-8'
    HEADER = 64
    DISCONNECT_MESSAGE = '!DISCONNECT'
    print('[NEW CONNECTION] {} connected.'.format(writer.get_extra_info('peername')))

    while True:
        msg_len = (await reader.read(HEADER)).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            command = (await reader.read(msg_len)).decode(FORMAT)
            if command == DISCONNECT_MESSAGE or command == 'exit':
                print(DISCONNECT_MESSAGE)
                break
            
            print('[{}] > Command {} Executed'.format(writer.get_extra_info('peername'), command))
            output = 'output: \n'
            output += subprocess.getoutput(command)
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

