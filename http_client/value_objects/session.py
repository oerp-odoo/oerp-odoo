from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from urllib3.util.retry import Retry

from odoo.addons.odootil.tools.parsing import parse_int_list, parse_to_list

if TYPE_CHECKING:
    from ..models.http_client_retry import HttpClientRetry


@dataclass(frozen=True)
class HttpSessionSettingsRetry:
    retry: Retry
    mount_prefixes: tuple[str] = ('https://',)

    @classmethod
    def from_record(cls, retry_record: HttpClientRetry) -> HttpSessionSettingsRetry:
        def format_number_param(n):
            if n < 0:
                return None
            return n

        retry_kw = {}
        if retry_record.allowed_methods:
            retry_kw['allowed_methods'] = frozenset(
                parse_to_list(retry_record.allowed_methods, clean_whitespace=True)
            )
        if retry_record.status_forcelist:
            retry_kw['status_forcelist'] = frozenset(
                parse_int_list(retry_record.status_forcelist)
            )
        retry = Retry(
            total=format_number_param(retry_record.retries_total),
            connect=format_number_param(retry_record.retries_connect),
            read=format_number_param(retry_record.retries_read),
            redirect=format_number_param(retry_record.retries_redirect),
            backoff_factor=retry_record.backoff_factor,
            raise_on_status=retry_record.raise_on_status,
            raise_on_redirect=retry_record.raise_on_redirect,
            **retry_kw,
        )
        return cls(
            retry=retry,
            mount_prefixes=tuple(
                parse_to_list(retry_record.mount_prefixes, clean_whitespace=True)
            ),
        )
