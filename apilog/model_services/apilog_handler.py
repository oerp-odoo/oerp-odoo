from __future__ import annotations

import json
import logging

from odoo import models
from odoo.fields import Command

from .. import const, value_objects as vo
from ..utils import form_filename, get_simple_call_stack, zip_with_base64

_logger = logging.getLogger(__name__)


class ApilogHandler(models.AbstractModel):
    _name = 'apilog.handler'
    _description = "API Log Handler"

    def handle(
        self,
        direction: vo.RequestDirection,
        source: str,
        request: vo.ApilogRequest,
        response: vo.ApilogResponse,
        extra_vals: dict | None = None,
    ):
        # Optimization to not go further, if no configs exist!
        ApilogConfig = self.env['apilog.config']
        if not ApilogConfig.has_any_config():
            return self.env['apilog.log']
        config_key = vo.ApilogMetaKey.from_request_response(
            direction=direction,
            source=source,
            request=request,
            response=response,
            call_stack=tuple(get_simple_call_stack()),
        )
        meta = ApilogConfig.get_apilog_metadata(config_key)
        if meta:
            log = self._create_log(request, response, meta, extra_vals=extra_vals)
            if log.config_id.debug:
                _logger.info("API Log (%s) created", log.name)
            return log
        return self.env['apilog.log']

    def _create_log(
        self,
        request: vo.ApilogRequest,
        response: vo.ApilogResponse,
        meta: vo.ApilogMetadata,
        extra_vals: dict | None = None,
    ):
        return self.env['apilog.log'].create(
            self._prepare_log_vals(request, response, meta, extra_vals=extra_vals)
        )

    def _prepare_log_vals(
        self,
        request: vo.ApilogRequest,
        response: vo.ApilogResponse,
        meta: vo.ApilogMetadata,
        extra_vals: dict | None = None,
    ):
        if extra_vals is None:
            extra_vals = {}
        cfg_id = meta.cfg_id
        vals = {
            'direction': meta.direction,
            'source': meta.source,
            'endpoint': request.endpoint,
            'http_verb': request.verb,
            'status_code': response.status_code,
            'request_body': request.body or False,
            'request_headers': json.dumps(request.headers),
            'response_headers': json.dumps(response.headers),
            'response_traceback': response.traceback or False,
            'config_id': cfg_id,
            **self._prepare_response_body_vals(
                response.body,
                self.env['apilog.config'].browse(cfg_id),
                response.headers,
            ),
        }
        if meta.label_ids:
            vals['label_ids'] = [Command.set(meta.label_ids)]
        vals.update(extra_vals)
        return vals

    def _prepare_response_body_vals(self, body: str, cfg, headers: dict):
        if not body:
            return {}
        base_name = const.RESPONSE_BASE_NAME
        if not cfg.response_body_as_file:
            return {base_name: body}
        filename = form_filename(base_name, headers)
        return {
            'response_body_file': zip_with_base64(filename, body.encode()),
            'response_body_filename': f'{base_name}.zip',
        }
