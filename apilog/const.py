import enum

JSON_INDENT = 2
MAX_CALL_STACK = 15
RESPONSE_BASE_NAME = 'response_body'


class Format(enum.StrEnum):
    JSON = 'json'


class ZipCompressLevel(enum.IntEnum):
    NO_COMPRESSION = 0
    FASTEST = 1
    DEFAULT = 6
    BEST = 9
