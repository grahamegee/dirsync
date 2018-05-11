import asyncio
import logging
import os

from .common import (
    FILE_PATH_LEN,
    FILE_LEN,
    COMMAND_LEN,
    COMMANDS
)


logging.basicConfig(level='DEBUG')
LOG = logging.getLogger('dirsync-server')

async def handle_client_connection(reader, writer):
    data = await reader.readexactly(COMMAND_LEN)
    command = COMMANDS[(int).from_bytes(data, 'big')]
    LOG.info('Command {}'.format(command))
    if command == 'FILE_ADD':
        await handle_file_add(reader, writer)
    elif command == 'FILE_DEL':
        await handle_file_del(reader, writer)


async def handle_file_add(reader, writer):
    data = await reader.readexactly(FILE_PATH_LEN)
    filepath_len = (int).from_bytes(data, 'big')
    LOG.debug(f'Filepath length: {filepath_len}')

    data = await reader.readexactly(filepath_len)
    filepath = data.decode()
    LOG.info(f'ADD File {filepath}')

    data = await reader.readexactly(FILE_LEN)
    file_len = (int).from_bytes(data, 'big')
    LOG.info(f'File length {file_len}')

    data = await reader.readexactly(file_len)

    write_file(filepath, data)
    writer.write(b'1')

    LOG.debug("Close the client socket")
    writer.close()

async def handle_file_del(reader, writer):
    data = await reader.readexactly(FILE_PATH_LEN)
    filepath_len = (int).from_bytes(data, 'big')

    data = await reader.readexactly(filepath_len)
    filepath = data.decode()
    LOG.info(filepath)

    delete_file(filepath)
    writer.write(b'1')

    LOG.debug("Close the client socket")
    writer.close()


def write_file(filepath, data):
    with open(filepath + '.sync', 'wb') as f:
        f.write(data)
    os.rename(f'./{filepath}.sync', f'./{filepath}')


def delete_file(filepath):
    os.remove(f'./{filepath}')


loop = asyncio.get_event_loop()
coro = asyncio.start_server(
    handle_client_connection, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)
LOG.info('Serving on {}'.format(server.sockets[0].getsockname()))

try:
    loop.run_forever()
except KeyboardInterrupt:
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
