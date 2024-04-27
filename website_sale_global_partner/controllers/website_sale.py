from odoo.http import request

from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def values_postprocess(self, order, mode, values, errors, error_msg):
        """Extend to force compay_id=False if is_global_partner is set."""
        res = super().values_postprocess(order, mode, values, errors, error_msg)
        if request.website.is_global_partner:
            res[0]['company_id'] = False
        return res
