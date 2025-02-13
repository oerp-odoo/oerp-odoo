from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from .. import const, value_objects as vo
from ..utils import match_number


class HttpClientConfig(models.Model):
    _name = 'http.client.config'
    _description = "HTTP Client Config"
    _rec_name = 'model_controller_id'

    model_controller_id = fields.Many2one(
        'ir.model',
        required=True,
        ondelete='cascade',
        string="Controller Model",
        index=True,
    )
    log_enabled = fields.Boolean(
        string="Logs Enabled",
        help="If checked, will save request/response data.",
    )
    log_limit_days = fields.Integer(
        "Days to Keep Logs", default=0, help="0 means no limit."
    )
    log_limit_count = fields.Integer(
        "Maximum Logs Count",
        default=0,
        help="Maximum number of log entries to keep. 0 means no limit.",
    )
    log_status_code_filter = fields.Char(
        "Filter Logs by Status Code",
        help="If specified, logs will be created only if status code matches the "
        + "expression. Expression can contain exact status codes or ranges of codes, "
        "separated by commas. For example: 200,201,!=404,>=400,<500. This will "
        + "match 200, 201 all codes greater than 400 or equal (except 404) up to 500 "
        "exclusive.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'model_controller_id_uniq',
            'unique (model_controller_id)',
            'The Controller Model must be unique!',
        )
    ]

    @api.constrains('model_controller_id')
    def _check_model_controller_id(self):
        for rec in self:
            model_name = rec.model_controller_id.model
            if not isinstance(
                self.env[model_name], type(self.env[const.BASE_CONTROLLER_MODEL])
            ):
                raise ValidationError(
                    _(
                        "Controller Model must inherit from %s!",
                        const.BASE_CONTROLLER_MODEL,
                    )
                )

    @api.constrains('log_status_code_filter')
    def _check_log_status_code_filter(self):
        for rec in self:
            expr = rec.log_status_code_filter
            if not expr:
                continue
            try:
                match_number(100, expr)
            except ValueError as e:
                raise ValidationError(e)

    @api.model
    @tools.ormcache('model_name')
    def get_cfg(self, model_name):
        cfg = self.search(self._get_config_domain(model_name), limit=1)
        if not cfg:
            return None
        return vo.Config(
            controller_model=model_name,
            log=vo.LogConfig(
                enabled=cfg.log_enabled,
                limit_days=cfg.log_limit_days,
                limit_count=cfg.log_limit_count,
                status_code_filter=cfg.log_status_code_filter,
            ),
        )

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        self.env.registry.clear_cache()
        return record

    def write(self, vals):
        result = super().write(vals)
        self.env.registry.clear_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.registry.clear_cache()
        return result

    def _get_config_domain(self, model_name: str):
        return [('model_controller_id.model', '=', model_name)]
