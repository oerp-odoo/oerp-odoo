import requests

from odoo import api, fields, models

from .. import const, value_objects as vo
from ..utils import match_number


class HttpClientLog(models.Model):
    _name = 'http.client.log'
    _description = "HTTP Client Log Request"

    name = fields.Char(compute='_compute_name')
    http_verb = fields.Selection(
        [
            (const.HttpVerb.GET, const.HttpVerb.GET),
            (const.HttpVerb.HEAD, const.HttpVerb.HEAD),
            (const.HttpVerb.OPTIONS, const.HttpVerb.OPTIONS),
            (const.HttpVerb.TRACE, const.HttpVerb.TRACE),
            (const.HttpVerb.PUT, const.HttpVerb.PUT),
            (const.HttpVerb.DELETE, const.HttpVerb.DELETE),
            (const.HttpVerb.POST, const.HttpVerb.POST),
            (const.HttpVerb.PATCH, const.HttpVerb.PATCH),
            (const.HttpVerb.CONNECT, const.HttpVerb.CONNECT),
        ],
        string="HTTP Verb",
        required=True,
        readonly=True,
    )
    endpoint = fields.Char(required=True, readonly=True)
    status_code = fields.Integer(required=True, readonly=True)
    model_controller_id = fields.Many2one(
        'ir.model',
        string="Controller Model",
        required=True,
        ondelete='cascade',
        readonly=True,
        index=True,
    )
    request_body = fields.Text(readonly=True)
    response_body = fields.Text(readonly=True)

    @api.depends('model_controller_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f'{rec.model_controller_id.model},{rec.id}'

    @api.model
    def handle_log(self, response: requests.Response, controller_model: str):
        cfg = self.env['http.client.config'].get_cfg(controller_model)
        if self._can_create_log(response, cfg):
            return self._create_log(response, controller_model)
        return self.browse()

    @api.model
    def _can_create_log(self, response: requests.Response, cfg: vo.Config):
        if cfg is None or not cfg.log.enabled:
            return False
        if cfg.log.status_code_filter:
            return match_number(response.status_code, cfg.log.status_code_filter)
        return True

    @api.model
    def _create_log(self, response: requests.Response, controller_model: str):
        vals = self._prepare_log_vals(response, controller_model)
        log = self.create(vals)
        return log

    @api.model
    def _prepare_log_vals(self, response: requests.Response, controller_model: str):
        request = response.request
        return {
            'model_controller_id': self.env['ir.model']._get(controller_model).id,
            'status_code': response.status_code,
            'http_verb': request.method,
            'endpoint': request.url,
            'request_body': request.body,
            'response_body': response.text,
        }
