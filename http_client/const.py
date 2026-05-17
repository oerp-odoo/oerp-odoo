from enum import Enum


class HttpVerb(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    PATCH = 'PATCH'
    CONNECT = 'CONNECT'


BASE_CONTROLLER_MODEL = 'http.client.controller'
FORMAT_RAW = 'raw'
FORMAT_JSON = 'json'
FORMAT_FORM = 'form'
MIMETYPE_JSON = 'application/json'
MIMETYPE_FORM = 'application/x-www-form-urlencoded'
B64_PADDING = '=='  # Should handle any base64 string.
DEFAULT_AUTH_TIMEOUT = 45  # in seconds
DEFAULT_TOTAL_RETRY = 10
DEFAULT_RETRY_MOUNT_PFX = 'https://'
DEFAULT_EXPIRE_DELTA = -60
DEFAULT_API_KEY_HEADER = 'ApiKey'
