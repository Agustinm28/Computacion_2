from asyncio import subprocess
import asyncio
import socketserver as ss
import argparse
from subprocess import Popen, PIPE
import subprocess


async def handle(reader, writer):
    print('[NEW CONNECTION] {} connected.'.format(writer.get_extra_info('peername')))

    filename = await reader.readline()
    filename = filename.decode().strip()
    print(f'[RECEIVING] File filename: {filename}')

    with open(filename, 'wb') as f:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            f.write(data)

    print(f'[SAVED] File saved as {filename}')
    writer.close()
    await writer.wait_closed()


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
