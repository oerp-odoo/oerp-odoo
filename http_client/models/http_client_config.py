from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from .. import const, value_objects as vo


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
    active = fields.Boolean(default=True)

    _model_controller_id_uniq = models.Constraint(
        'unique (model_controller_id)', "The Controller Model must be unique!"
    )

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

    @api.model
    @tools.ormcache('model_name')
    def get_cfg(self, model_name):
        cfg = self.search(self._get_config_domain(model_name), limit=1)
        if not cfg:
            return None
        return vo.Config(
            controller_model=model_name,
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
