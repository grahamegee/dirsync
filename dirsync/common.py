FILE_PATH_LEN = 2
FILE_LEN = 8
COMMAND_LEN = 1

FILE_ADD = OK = b'\x01'
FILE_DEL = ERROR = b'\x02'

RESPONSE_CODES = {
    b'\x01': 'OK',
    b'\x02': 'ERROR'
}
