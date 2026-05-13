import json

from odoo import api, fields, models

from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import const, utils, value_objects as vo


class ApilogLog(models.Model):
    _name = 'apilog.log'
    _description = "API Log - Log"
    _order = "create_date desc, id desc"

    name = fields.Char(compute='_compute_name')
    http_verb = fields.Selection(
        [
            (HttpVerb.GET, HttpVerb.GET),
            (HttpVerb.HEAD, HttpVerb.HEAD),
            (HttpVerb.OPTIONS, HttpVerb.OPTIONS),
            (HttpVerb.TRACE, HttpVerb.TRACE),
            (HttpVerb.PUT, HttpVerb.PUT),
            (HttpVerb.DELETE, HttpVerb.DELETE),
            (HttpVerb.POST, HttpVerb.POST),
            (HttpVerb.PATCH, HttpVerb.PATCH),
            (HttpVerb.CONNECT, HttpVerb.CONNECT),
        ],
        string="HTTP Verb",
        index=True,
        required=True,
        readonly=True,
    )
    endpoint = fields.Char(required=True, readonly=True, index=True)
    status_code = fields.Integer(
        required=True,
        readonly=True,
        index=True,
        aggregator=None,
    )
    direction = fields.Selection(
        [
            (vo.RequestDirection.INCOMING, "Incoming"),
            (vo.RequestDirection.OUTGOING, "Outgoing"),
        ],
        index=True,
        required=True,
        readonly=True,
    )
    source = fields.Selection(
        lambda s: s.env['apilog.config'].prepare_source_selection(),
        index=True,
        required=True,
        readonly=True,
    )
    config_id = fields.Many2one(
        'apilog.config', required=True, index=True, readonly=True
    )
    request_body = fields.Text(readonly=True)
    response_body = fields.Text(readonly=True)
    # Only saved when response_body_as_file option is used.
    response_body_file = fields.Binary(attachment=True)
    response_body_filename = fields.Char()
    response_body_value = fields.Binary(compute='_compute_response_body_value')
    request_headers = fields.Text(readonly=True, required=True, default="{}")
    response_headers = fields.Text(readonly=True, required=True, default="{}")
    response_traceback = fields.Text(readonly=True)
    request_body_formatted = fields.Text(compute='_compute_formatted_data')
    response_body_formatted = fields.Text(compute='_compute_formatted_data')
    request_headers_formatted = fields.Text(compute='_compute_formatted_data')
    response_headers_formatted = fields.Text(compute='_compute_formatted_data')
    res_model = fields.Char("Model", index=True, readonly=True)
    res_id = fields.Integer("Record ID", index=True, readonly=True)
    label_ids = fields.Many2many(
        'apilog.label',
        'apilog_log_label_rel',
        'log_id',
        'label_id',
        string="Labels",
        readonly=True,
    )

    @api.depends('endpoint', 'http_verb', 'status_code')
    def _compute_name(self):
        for rec in self:
            rec.name = f'{rec.http_verb} {rec.endpoint} ({rec.status_code})'

    @api.depends('response_body', 'response_body_file')
    def _compute_response_body_value(self):
        for log in self:
            if log.response_body:
                log.response_body_value = log.response_body.encode()
            elif log.response_body_file:
                log.response_body_value = log._read_response_body_file()
            else:
                log.response_body_value = False

    @api.depends('request_body', 'request_headers', 'response_body', 'response_headers')
    def _compute_formatted_data(self):
        ApilogFormatter = self.env['apilog.formatter']
        for log in self:
            log.update(
                {
                    'request_body_formatted': ApilogFormatter.format(
                        log.request_body, log.request_headers
                    ),
                    'request_headers_formatted': ApilogFormatter.format_json(
                        log.request_headers
                    ),
                    'response_body_formatted': ApilogFormatter.format(
                        log.response_body, log.response_headers
                    ),
                    'response_headers_formatted': ApilogFormatter.format_json(
                        log.response_headers
                    ),
                }
            )

    def _read_response_body_file(self) -> bytes:
        self.ensure_one()
        filename = utils.form_filename(
            const.RESPONSE_BASE_NAME, json.loads(self.response_headers)
        )
        with utils.unzip_from_base64(self.response_body_file) as zf:
            return zf.read(filename)
