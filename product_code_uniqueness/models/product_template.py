from odoo import api, models

from ..utils import build_default_code


class ProductTemplate(models.Model):
    """Extend to make default_code unique."""

    _inherit = 'product.template'

    @api.constrains('default_code', 'company_id')
    def _check_default_code(self):
        """Check if product's default_code is unique."""
        for product in self:
            if len(product.product_variant_ids) == 1:
                product.product_variant_ids._check_default_code()

    def copy_data(self, default=None):
        """Extend to copy `default_code` with ' (copy)' extension."""
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'default_code' not in default:
            for template, vals in zip(self, vals_list):
                vals['default_code'] = build_default_code(template, default=default)
        return vals_list
