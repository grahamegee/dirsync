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

Navigate to the directory that you want to keep up to date and start the server.
```bash
cd <path to dir>
python -m dirsync.client
```

