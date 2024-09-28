import ast

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class BaseData(models.Model):
    """Model to map data for records that are to be created."""

    _name = 'base.data'
    _description = "Base Data"

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade')
    defaults = fields.Text(required=True, default="{}")
    label_ids = fields.Many2many(
        'base.data.label',
        'base_data_label_rel',
        'data_id',
        'label_id',
    )
    active = fields.Boolean(default=True)

    @api.constrains('name', 'model_id', 'label_ids')
    def _check_data_key(self):
        BaseData = self.browse()
        for rec in self:
            matches = BaseData._find_match(
                rec.name,
                rec.model_id.model,
                labels=frozenset(rec.label_ids.mapped('name')),
            )
            if len(matches) > 1:
                raise ValidationError(
                    _("Data keys must be unique (name, model, labels)!")
                )

    @api.constrains('defaults')
    def _check_defaults(self):
        msg = _("Defaults must be dictionary.")
        for rec in self:
            if rec.defaults:
                try:
                    defaults = ast.literal_eval(rec.defaults)
                    if not isinstance(defaults, dict):
                        raise ValidationError(msg)
                except Exception as e:
                    raise ValidationError(msg + _(" Error: %s", e))

    @api.model
    @tools.ormcache('name', 'model', 'labels')
    # Can't use typehints here, because ormcache does not support it..
    def get_data(self, name, model, labels=frozenset()):
        rec = self._find_match(name, model, labels=labels)
        if not rec:
            return {}
        return ast.literal_eval(rec.defaults)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.get_data.clear_cache(self)
        return recs

    def write(self, vals):
        res = super().write(vals)
        self.get_data.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self.get_data.clear_cache(self)
        return res

    @api.model
    def _find_match(self, name: str, model: str, labels: frozenset = frozenset()):
        domain = self._prepare_domain(name, model, labels=labels)
        recs = self.search(domain)
        matched_recs = self.browse()
        # We need to match it by exact labels, not just if it includes some, so it is
        # tricky do to that via domain. Using filtering instead.
        for rec in recs:
            if set(rec.label_ids.mapped('name')) == labels:
                matched_recs |= rec
        return matched_recs

    @api.model
    def _prepare_domain(self, name: str, model: str, labels: frozenset = frozenset()):
        return [
            ('name', '=', name),
            ('model_id.model', '=', model),
        ]
