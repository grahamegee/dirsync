# dirsync

Implementations of a client and server for syncing directories over IP.

## Install

Clone the repo

``` bash
git clone git@github.com:grahamegee/dirsync.git
cd dirsync
```

make a python 3 virtualenv.

``` bash
mkvirtualenv -p python3 <name>
```

PIP install

```bash
pip install -e .
```

## Usage

* Make sure your virtualenv is active.
* Start the server first.
* Start the client second.

### Server

Navigate to the directory that you want to keep up to date and start the server.
```bash
cd <path to dir>
python -m dirsync.server
```

### Client 

Navigate to the directory that you want to keep up to date and start the client.
```bash
cd <path to dir>
python -m dirsync.client
```

You can optionally set the server-ip with `--server-ip`.

## TODO

* Make the directory configurable on the server and client (command-line arg).
  This will involve getting rid of the handy `asyncio.start_server`
  convenience function unfortunately.
* Handle file deletions that happen when the client is down.
  This requires extending the protocol to allow the client and server to
  communicate their respective file trees.
* Handle sub-directories.
  * client: look for `[CREATE, IS_DIR]` flags and recursively call `watch`.
  * server: implement mkdir
* Handle large files and optimise data transfer.
  These go hand in hand:
  * Open large file in smaller chunks.
  * Negotiate checksums on the chunks rather than full files.

