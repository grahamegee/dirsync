import asyncio
import logging
import aionotify
import os
import hashlib
import argparse

from .common import (
    FILE_PATH_LEN,
    FILE_LEN,
    COMMAND_LEN,
    FILE_ADD,
    FILE_DEL,
    OK,
    GOT,
    RESPONSE_CODES
)


logging.basicConfig(level='DEBUG')
LOG = logging.getLogger('dirsync-client')


async def touch():
    # TODO: Handle nested directories
    # FIXME: Handle deleted files during client downtime. This will involve
    # A more complicated protocol whereby the client and server exchange
    # filepath trees and look for differences.
    with os.scandir('./') as it:
        for entry in it:
            if entry.is_file():
                open(entry.name, 'a').close()


async def watch(loop, path, server_ip):
    watcher = aionotify.Watcher()
    watcher.watch(path, aionotify.Flags.DELETE | aionotify.Flags.CLOSE_WRITE)
    await watcher.setup(loop)
    while True:
        event = await watcher.get_event()
        flags = aionotify.Flags.parse(event.flags)
        LOG.debug(f'{event.name}, {flags}')

        # TODO Handle directory creation and set up a new task to monitor
        # sub directories. Preliminary investigation suggests another call
        # to loop.create_event(watch(loop, path + event.name + '/') will
        # work.
        if flags == [aionotify.Flags.CLOSE_WRITE]:
            await send_file(loop, path + event.name, server_ip)
        elif flags == [aionotify.Flags.DELETE]:
            await send_delete_file(loop, path + event.name, server_ip)


async def send_delete_file(loop, filepath, server_ip):
    LOG.info(f'DELETE {filepath}')
    reader, writer = await asyncio.open_connection(
        server_ip, 8888, loop=loop)

    filepath = filepath.encode()
    filepath_len = len(filepath).to_bytes(FILE_PATH_LEN, 'big')
    LOG.debug(f'Filepath length: {filepath_len}')

    writer.write(FILE_DEL + filepath_len + filepath)
    writer.drain()

    response = await reader.readexactly(1)
    LOG.info('Received: %r' % RESPONSE_CODES[response])

    LOG.debug('Close the socket')
    writer.close()


async def send_file(loop, filepath, server_ip):
    print('XXXX', server_ip)
    LOG.info(f'ADD {filepath}')
    reader, writer = await asyncio.open_connection(
        server_ip, 8888, loop=loop)
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
    # This handles temporary files maybe? That's is at least what it looks like.
    except FileNotFoundError:
        return
    filepath = filepath.encode()
    filepath_len = len(filepath).to_bytes(FILE_PATH_LEN, 'big')
    file_len = len(file_bytes).to_bytes(FILE_LEN, 'big')
    checksum = hashlib.md5(file_bytes).hexdigest().encode()
    LOG.debug(f'Filepath length: {filepath_len}')
    LOG.info(f'SEND {filepath}')
    LOG.debug(f'File length: {file_len}')

    writer.write(FILE_ADD + filepath_len + filepath + checksum)
    writer.drain()
    response = await reader.readexactly(1)
    if response == GOT:
        LOG.info(f'File {filepath} already up to date')
    elif response == OK:
        LOG.info(f'Sending file data for {filepath}')
        writer.write(file_len + file_bytes)
        writer.drain()

        data = await reader.readexactly(1)
        LOG.info('Received: %r' % RESPONSE_CODES[data])

    LOG.debug('Close the socket')
    writer.close()

parser = argparse.ArgumentParser('Directory sync client')
parser.add_argument('--server-ip', default='127.0.0.1', dest='server_ip')
args = parser.parse_args()
loop = asyncio.get_event_loop()
loop.create_task(watch(loop, './', args.server_ip))
loop.create_task(touch())
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
