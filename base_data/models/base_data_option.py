import ast

from odoo import _, api, fields, models

from ..utils import validate_dict_str


class BaseDataOption(models.Model):
    _name = 'base.data.option'
    _description = "Base Data Option"

    name = fields.Char(required=True, string="Key")
    value = fields.Char(required=True)
    base_data_id = fields.Many2one('base.data', required=True, ondelete='cascade')
    data = fields.Text(required=True, default="{}")

    @api.constrains('data')
    def _check_defaults(self):
        msg = _("Data must be a dictionary.")
        for rec in self:
            if rec.data:
                validate_dict_str(rec.data, msg)

    def get_data(self, options=frozenset[tuple[str, str]]):
        data = {}
        for opt in self._match_option(options):
            data.update(ast.literal_eval(opt.data))
        return data

    def _match_option(self, options=frozenset[tuple[str, str]]):
        for key, val in options:
            for opt in self:
                if opt.name == key and opt.value == val:
                    yield opt

    _sql_constraints = [
        (
            'name_value_base_data_id_uniq',
            'unique (name, value, base_data_id)',
            'Key and Value must be unique per Base Data record!',
        )
    ]
