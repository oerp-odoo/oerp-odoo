from odoo import models


class ProductProduct(models.Model):
    """Extend to add retrieve_hs_code method."""

    _inherit = 'product.product'

    def retrieve_hs_code(self, country_code=None):
        """Retrieve related HS code for country or fallback to default.

        If country is not specified or can't find code for specific
        country, will fallback to origin country HS code or to HS code
        specified directly on product.template.

        Args:
            country_code (str): country code to use in search
                (default: {None}).

        Returns:
            HS Code.
            str

        """
        # Case for convenience.
        if not self:
            return False
        self.ensure_one()
        return self.product_tmpl_id._retrieve_hs_code(country_code=country_code)
