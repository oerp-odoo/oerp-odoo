from odoo import _, api, models
from odoo.exceptions import ValidationError

from ..utils import build_default_code, search_multicompany_count
from .res_config_settings import CFG_PARAM_PRODUCT_CODE_UNIQUE

OP_EQ_MAP = {True: '=ilike', False: '='}


class ProductProduct(models.Model):
    """Extend to make default_code unique."""

    _inherit = 'product.product'

    def copy_data(self, default=None):
        """Extend to copy `default_code` with ' (copy)' extension."""
        return super().copy_data(build_default_code(self, default))

    @api.constrains('default_code', 'company_id')
    def _check_default_code(self):
        """Check if product's default_code is unique."""
        # Ignore empty codes and check if product code uniqueness is
        # disabled/enabled/enabled_insensitive
        uniqueness = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_PRODUCT_CODE_UNIQUE, default='disabled')
        )
        if uniqueness in ('enabled', 'enabled_insensitive'):
            case_insensitive = uniqueness == 'enabled_insensitive'
            for product in self.filtered('default_code'):
                domain = [
                    (
                        'default_code',
                        OP_EQ_MAP[case_insensitive],
                        product.default_code,
                    )
                ]
                matches = search_multicompany_count(
                    product.sudo(),
                    domain=domain,
                    options={
                        'multi_comp_rule_xml_id': 'product.product_comp_rule',
                        'company_id': product.company_id.id,
                    },
                )
                if matches > 1:
                    raise ValidationError(
                        _(
                            "Product code (%s) must be unique per company! "
                            "There might be an archived product with the "
                            "same code too.",
                            product.default_code,
                        )
                    )
