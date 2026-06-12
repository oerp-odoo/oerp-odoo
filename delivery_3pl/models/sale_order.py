from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tpl_service_id = fields.Many2one(
        'tpl.service',
        string="3PL Service",
        compute='_compute_tpl_service_id',
        store=True,
        readonly=False,
        precompute=True,
        check_company=True,
    )
    tpl_integration = fields.Selection(related='tpl_service_id.integration', store=True)
    tpl_identifier = fields.Char(string="3PL Identifier", copy=False, readonly=True)
    tpl_status = fields.Selection(
        [
            ('progress', "In Progress"),
            ('done', "Done"),
            ('cancel', "Cancelled"),
        ],
        copy=False,
        readonly=True,
    )

    _tpl_identifier_uniq = models.Constraint(
        'unique(tpl_identifier, tpl_integration)',
        'The 3PL Identifier must be unique per Integration!',
    )

    @api.depends('company_id', 'order_line')
    def _compute_tpl_service_id(self):
        for sale in self:
            service = self.env['tpl.service'].get_3pl_service(
                sale, raise_not_found=False
            )
            sale.tpl_service_id = service

    @api.depends('tpl_service_id')
    def _compute_warehouse_id(self):
        super()._compute_warehouse_id()
        for sale in self:
            warehouse = sale.tpl_service_id.warehouse_id
            if warehouse:
                sale.warehouse_id = warehouse

    def action_confirm(self):
        res = super().action_confirm()
        SaleOrder3Pl = self.env['tpl.sale.order']
        for sale in self.filtered('tpl_service_id'):
            SaleOrder3Pl.confirm(sale)
        return res

    def action_cancel(self):
        res = super().action_cancel()
        SaleOrder3Pl = self.env['tpl.sale.order']
        for sale in self.filtered('tpl_service_id'):
            SaleOrder3Pl.cancel(sale)
        return res

    def action_draft(self):
        res = super().action_draft()
        SaleOrder3Pl = self.env['tpl.sale.order']
        for sale in self.filtered('tpl_service_id'):
            SaleOrder3Pl.draft(sale)
        return res

    def action_3pl_sync_shipment_status(self):
        self.ensure_one()
        return self.env['tpl.sale.order'].sync_shipment_status(self)
