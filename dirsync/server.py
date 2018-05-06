import asyncio
import logging

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

    data = await reader.readexactly(FILE_PATH_LEN)
    filepath_len = (int).from_bytes(data, 'big')

    data = await reader.readexactly(filepath_len)
    filepath = data.decode()
    print(filepath)

    data = await reader.readexactly(FILE_LEN)
    file_len = (int).from_bytes(data, 'big')
    print(file_len)

    data = await reader.readexactly(file_len)
    print(data)

    writer.write(b'1')

    LOG.debug("Close the client socket")
    writer.close()


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
