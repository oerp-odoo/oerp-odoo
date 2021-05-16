import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


HS_COUNTRY_CODE_RE = r'^\d+$'


class ProductTemplateHsCode(models.Model):
    """Model to store different HS code parts per country."""

    _name = 'product.template.hs.code'
    _description = "Product Template HS Code"

    name = fields.Char(
        compute='_compute_name', string="Country HS Code", store=True
    )
    code = fields.Char("Suffix")
    product_tmpl_id = fields.Many2one(
        'product.template',
        string="Product Template",
        required=True
    )
    country_id = fields.Many2one('res.country', required=True)
    is_origin_country = fields.Boolean(string="Country of Origin")

    _sql_constraints = [
        (
            'country_id_uniq',
            'unique (country_id, product_tmpl_id)',
            "The country must be unique per related product template !",
        )
    ]

    @api.depends('code', 'product_tmpl_id.hs_code')
    def _compute_name(self):
        for hs in self:
            hs.name = '%s%s' % (
                hs.product_tmpl_id.hs_code or '', hs.code or ''
            )

    @api.constrains('code')
    def _check_country_hs_code(self):
        for hs in self.filtered('code'):
            if not re.match(HS_COUNTRY_CODE_RE, hs.code):
                raise ValidationError(
                    _("Country HS Code Part must be digits only. Got"
                        " '%s' instead") % hs.code
                )

    @api.constrains('is_origin_country', 'product_tmpl_id')
    def _check_is_origin_country(self):
        for hs in self.filtered('is_origin_country'):
            if len(
                hs.product_tmpl_id.hs_code_ids.filtered('is_origin_country')
            ) > 1:
                raise ValidationError(
                    _("Only one HS Code can have Origin Country!")
                )

    def _filter_hs_code_by_country(self, country_code):
        return self.filtered(
            lambda r: r.country_id.code.upper() == country_code.upper()
        )

    def _filter_hs_code(self, country_code=None):
        hs_origin = self.filtered('is_origin_country')
        if not country_code:
            return hs_origin
        hs_country = self._filter_hs_code_by_country(country_code)
        if not hs_country:
            return hs_origin
        return hs_country
