from __future__ import annotations

import dataclasses
import enum

import odoo.http

from odoo.addons.odootil.value_objects.http import HttpVerb

from .utils import get_data_safely, sanitize_headers


class RequestDirection(str, enum.Enum):
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'


@dataclasses.dataclass(frozen=True)
class ApilogRequest:
    endpoint: str
    verb: HttpVerb
    body: str | None = None
    _headers: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_httprequest(cls, httprequest: odoo.http.HttpRequest):
        return cls(
            endpoint=httprequest.url,
            verb=httprequest.method.upper(),
            body=get_data_safely(httprequest, as_text=True),
            _headers=httprequest.headers,
        )

    @property
    def headers(self):
        return sanitize_headers(self._headers)


@dataclasses.dataclass(frozen=True)
class ApilogResponse:
    status_code: int
    body: str | None = None
    traceback: str | None = None
    _headers: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_werkzeug_response(cls, response: odoo.http.Response):
        kw = {}
        if hasattr(response, 'traceback'):
            kw['traceback'] = response.traceback
        return cls(
            status_code=response.status_code,
            body=get_data_safely(response, as_text=True),
            _headers=response.headers,
            **kw,
        )

    @property
    def headers(self):
        return sanitize_headers(self._headers)


@dataclasses.dataclass(frozen=True)
class ApilogMetaKey:
    direction: RequestDirection
    source: str
    endpoint: str
    verb: HttpVerb
    status_code: int
    call_stack: tuple[tuple[str, str]]
    auth_fingerprint: str = ''

    @classmethod
    def from_request_response(
        cls,
        direction: RequestDirection,
        source: str,
        request: ApilogRequest,
        response: ApilogResponse,
        call_stack: tuple,
    ):
        return cls(
            direction=direction,
            source=source,
            endpoint=request.endpoint,
            verb=request.verb,
            status_code=response.status_code,
            call_stack=call_stack,
            auth_fingerprint=request.headers.get('Authorization') or '',
        )


@dataclasses.dataclass(frozen=True)
class ApilogMatcherInput:
    endpoint: str
    verb: HttpVerb
    status_code: int
    call_stack: tuple[tuple[str, str]] = ()
    auth_fingerprint: str = ''


@dataclasses.dataclass(frozen=True)
class ApilogMetadata:
    cfg_id: int
    direction: RequestDirection
    source: str
    label_ids: list[int] | None = None


@dataclasses.dataclass(frozen=True)
class ApilogRotatorConfig:
    apilog_cfg_id: int
    limit_days: int = 0
    limit_count: int = 0

    @classmethod
    def from_apilog_config(cls, cfg):
        return cls(
            apilog_cfg_id=cfg.id,
            limit_days=cfg.log_limit_days,
            limit_count=cfg.log_limit_count,
        )
