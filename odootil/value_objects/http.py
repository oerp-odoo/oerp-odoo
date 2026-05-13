import enum


class HttpVerb(str, enum.Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    PATCH = 'PATCH'
    CONNECT = 'CONNECT'
