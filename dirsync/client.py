import asyncio
import logging
import aionotify
import os

from .common import (
    FILE_PATH_LEN,
    FILE_LEN,
    COMMAND_LEN)


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


async def watch(loop, path):
    watcher = aionotify.Watcher()
    watcher.watch(
        path,
        (
            aionotify.Flags.MODIFY |
            aionotify.Flags.CREATE |
            aionotify.Flags.DELETE |
            aionotify.Flags.ATTRIB |
            aionotify.Flags.CLOSE_WRITE

        ))
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
            await send_file(loop, path + event.name)
        elif flags == [aionotify.Flags.DELETE]:
            await send_delete_file(loop, path + event.name)


async def send_delete_file(loop, filepath):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888, loop=loop)
    filepath = filepath.encode()
    filepath_len = len(filepath).to_bytes(FILE_PATH_LEN, 'big')
    command = (2).to_bytes(COMMAND_LEN, 'big')
    LOG.info(f'DELETE {filepath}')
    LOG.debug(f'Filepath length: {filepath_len}')

    writer.write(command + filepath_len + filepath)
    writer.drain()

    data = await reader.read(100)
    LOG.info('Received: %r' % data.decode())

    LOG.debug('Close the socket')
    writer.close()


async def send_file(loop, filepath):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888, loop=loop)
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
    # This handles temporary files maybe? That's is at least what it looks like.
    except FileNotFoundError:
        return
    filepath = filepath.encode()
    filepath_len = len(filepath).to_bytes(FILE_PATH_LEN, 'big')
    file_len = len(file_bytes).to_bytes(FILE_LEN, 'big')
    command = (1).to_bytes(COMMAND_LEN, 'big')
    LOG.debug(f'Filepath length: {filepath_len}')
    LOG.info(f'SEND {filepath}')
    LOG.debug(f'File length: {file_len}')

    writer.write(command + filepath_len + filepath + file_len + file_bytes)
    writer.drain()

    data = await reader.read(100)
    LOG.info('Received: %r' % data.decode())

    LOG.debug('Close the socket')
    writer.close()


loop = asyncio.get_event_loop()
loop.create_task(watch(loop, './'))
loop.create_task(touch())
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
