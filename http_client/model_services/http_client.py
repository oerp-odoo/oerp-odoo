import dataclasses
import logging

from odoo import models

from ..utils import get_next_link
from ..value_objects.request import RequestInput

_logger = logging.getLogger(__name__)


class HttpClient(models.AbstractModel):
    _name = 'http.client'
    _description = "HTTP Client"

    def send(self, inp: RequestInput):
        response = self.env['http.client.transport'].request(inp)
        self._check_response(response, inp)
        return response

    def send_paginated(self, link_key: str, inp: RequestInput):
        results = []
        while True:
            response = self.send(inp)
            results.append(response)
            next_link = get_next_link(response, link_key)
            if next_link is None:
                break
            inp = dataclasses.replace(inp, url=next_link, relative_path=None)
        return results

    def raise_response_error(self, response, exc):
        msg_pattern, args = self._prepare_response_error_data(response)
        error_msg = msg_pattern % args
        raise exc(error_msg)

    def _check_response(self, response, inp: RequestInput):
        """Check if returned response is successful."""
        if response.ok:
            self._on_response_ok(response, inp)
        else:
            self._on_response_error(response, inp)

    def _on_response_ok(self, response, inp: RequestInput):
        """Override to add extra logic when response is successful."""

    def _on_response_error(self, response, inp: RequestInput):
        profile = inp.profile
        exc_path = profile.non_ok_exception_path
        if not exc_path:
            return self._log_response_error(response)
        exc = profile.load_non_ok_exception()
        self.raise_response_error(response, exc)

    def _prepare_response_error_data(self, response):
        msg_pattern = (
            "Endpoint '%s' call failed. Method: %s, Error Code: %s, Response: %s"
        )
        return (
            msg_pattern,
            (
                response.url,
                response.request.method,
                response.status_code,
                response.text,
            ),
        )

    def _log_response_error(self, response):
        msg_pattern, error_data = self._prepare_response_error_data(response)
        _logger.error(msg_pattern, *error_data)
