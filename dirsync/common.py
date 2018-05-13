FILE_PATH_LEN = 2
FILE_LEN = 8
COMMAND_LEN = 1
CHECKSUM_LEN = 32

FILE_ADD = OK = b'\x01'
FILE_DEL = ERROR = b'\x02'
GOT = b'\x03'

RESPONSE_CODES = {
    b'\x01': 'OK',
    b'\x02': 'ERROR',
    b'\x03': 'GOT'
}
