import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

HS_CODE_RE = r'^\d{6}$'


class ProductTemplate(models.Model):
    """Extend to relate with product.template.hs.code."""

    _inherit = 'product.template'

    hs_code_ids = fields.One2many(
        'product.template.hs.code',
        'product_tmpl_id',
        string="HS Codes",
    )
    country_origin_id = fields.Many2one(
        'res.country',
        compute='_compute_country_origin_id',
        string="Country of Origin",
        store=True,
    )

    @api.depends('hs_code_ids.country_id', 'hs_code_ids.is_origin_country')
    def _compute_country_origin_id(self):
        for tmpl in self:
            hs = tmpl.hs_code_ids.filtered(lambda r: r.is_origin_country)[:1]
            tmpl.country_origin_id = hs.country_id

    @api.constrains('hs_code')
    def _check_hs_code(self):
        msg = _("HS Code must be 6 digits. Got '%s' instead")
        for tmpl in self.filtered('hs_code_ids'):
            hs_code = tmpl.hs_code
            if not hs_code or not re.match(HS_CODE_RE, hs_code):
                raise ValidationError(msg % hs_code)

    def _retrieve_hs_code(self, country_code=None):
        self.ensure_one()
        hs = self.hs_code_ids._filter_hs_code(country_code=country_code)
        if not hs:
            return self.hs_code
        return hs.name
