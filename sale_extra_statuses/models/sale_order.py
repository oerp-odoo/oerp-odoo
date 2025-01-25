from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_status = fields.Selection(
        [
            ('rfq', "RFQ"),
            ('confirmed', "Confirmed"),
            ('received', "Received"),
            ('done', "Done"),
        ],
        compute='_compute_purchase_status',
        store=True,
    )
    delivery_progress = fields.Float(
        compute='_compute_delivery_progress', digits=(16, 2), store=True
    )
    production_progress = fields.Float(
        compute='_compute_production_progress', digits=(16, 2), store=True
    )
    component_progress = fields.Float(
        compute='_compute_component_availability', digits=(16, 2), store=True
    )
    component_availability_state = fields.Selection(
        [
            ('available', "Available"),
            ('unavailable', "Unavailable"),
            ('expected', "Expected"),
            ('late', "Late"),
        ],
        compute='_compute_component_availability',
        store=True,
    )

    @api.depends(
        'purchase_from_primary_ids.state',
        'picking_from_primary_ids.state',
    )
    def _compute_purchase_status(self):
        SOPS = self.env['sale.order.purchase.status']
        for rec in self:
            rec.purchase_status = SOPS.get_status(rec)

    @api.depends('picking_ids.state')
    def _compute_delivery_progress(self):
        SODP = self.env['sale.order.delivery.progress']
        for rec in self:
            rec.delivery_progress = SODP.get_progress(rec)

    @api.depends('production_from_primary_ids.state')
    def _compute_production_progress(self):
        SOPP = self.env['sale.order.production.progress']
        for rec in self:
            rec.production_progress = SOPP.get_progress(rec)

    @api.depends(
        'commitment_date',
        'production_from_primary_ids.state',
        'production_from_primary_ids.reservation_state',
        'production_from_primary_ids.move_raw_ids',
        'production_from_primary_ids.move_raw_ids.forecast_availability',
        'production_from_primary_ids.move_raw_ids.forecast_expected_date',
    )
    def _compute_component_availability(self):
        SOCA = self.env['sale.order.component.availability']
        for rec in self:
            state, progress = SOCA.get_availability_info(rec)
            rec.update(
                {
                    'component_availability_state': state,
                    'component_progress': progress,
                }
            )
