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


class LogMode(str, Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    BOTH = 'both'


DEFAULT_AUTH_TIMEOUT = 45  # in seconds
BASE_CONTROLLER_MODEL = 'http.client.controller'
