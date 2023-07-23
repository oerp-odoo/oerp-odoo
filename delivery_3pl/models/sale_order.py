from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_3pl_service(self, name=None, raise_not_found=True):
        """Extend to implement way to find specific 3PL service.

        When service name is provided, only that service should be
        searched!
        """
        self.ensure_one()
        matchers_map = self.get_3pl_service_matchers()
        if name is not None:
            try:
                # If we got single name, we check only that single service!
                matchers_map = {name: matchers_map[name]}
            except KeyError:
                raise ValidationError(_("No 3PL service found with name %s", name))
        for service_matcher in matchers_map.values():
            service = service_matcher()
            if service:
                return service
        if raise_not_found:
            raise ValidationError(
                _(
                    "No 3PL service found for sale order %s. Make sure"
                    + " it is created and active.",
                    self.name,
                )
            )
        return self.env['tpl.service']

    def get_3pl_service_matchers(self):
        """Extend to register 3PL service matcher.

        Key is unique string and value is sale.order record bound method
        that will find service.
        """
        self.ensure_one()
        return {}

    def get_3pl_warehouse_data(self):
        """Find 3PL warehouse from specific 3PL service."""
        self.ensure_one()
        service = self.get_3pl_service(raise_not_found=False)
        if not service:
            return (self.env['stock.warehouse'], False)
        return service.get_warehouse_data()

    @api.model
    def create(self, vals):
        wh_id_in_vals = 'warehouse_id' in vals
        sale = super().create(vals)
        # Because there can be some important data set during creation,
        # we wait till record is created and then we do update. Its not
        # very efficient, but more consistent.
        warehouse, forced = sale.get_3pl_warehouse_data()
        if warehouse and (not wh_id_in_vals or forced):
            sale.warehouse_id = warehouse.id
        return sale
