import asyncio
import logging

from .common import (
    FILE_PATH_LEN,
    FILE_LEN,
    COMMAND_LEN)

FILEPATH='./a.txt'

logging.basicConfig(level='DEBUG')
LOG = logging.getLogger('dirsync-client')


async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888, loop=loop)
    LOG.info('Send: %r' % message)
    with open(FILEPATH, 'rb') as f:
        file_bytes = f.read()
    filepath = FILEPATH.encode()
    filepath_len = len(filepath).to_bytes(FILE_PATH_LEN, 'big')
    file_len = len(file_bytes).to_bytes(FILE_LEN, 'big')
    command = (1).to_bytes(COMMAND_LEN, 'big')
    LOG.info(filepath_len)
    LOG.info(filepath)
    LOG.info(file_len)
    LOG.info(file_bytes)

    writer.write(command + filepath_len + filepath + file_len + file_bytes)
    writer.drain()

    data = await reader.read(100)
    LOG.info('Received: %r' % data.decode())

    LOG.debug('Close the socket')
    writer.close()


message = 'Hello World!'
loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(message, loop))
loop.close()
