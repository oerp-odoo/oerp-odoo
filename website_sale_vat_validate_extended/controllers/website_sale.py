from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtended(WebsiteSale):
    """Extend to add extra fields for _get_vat_validation_fields."""

    def _get_vat_validation_fields(self, data):
        res = super()._get_vat_validation_fields(data)
        res.update(
            {
                'is_company': True,
                # To show actual partner name in error message, instead of just
                # 'False'.
                'name': data.get('company_name') or data.get('name') or False,
            }
        )
        return res
