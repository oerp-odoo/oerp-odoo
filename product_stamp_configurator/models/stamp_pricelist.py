from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..const import DP_PRICE


class StampPricelist(models.Model):
    _name = 'stamp.pricelist'
    _description = "Stamp Pricelist"

    name = fields.Char(required=True)
    item_ids = fields.One2many(
        'stamp.pricelist.item',
        'stamp_pricelist_id',
        string="Items",
    )
    # Area term makes more sense here, but keeping Size in label as its
    # more familiar to users.
    min_area = fields.Float(
        "Minimum Size, cm2",
        help="Will use this size to calculate price if entered size in "
        + "configurator is lower than this. Keep 0 to not use it.",
    )
    # TODO: it might make more sense to have these options per pricelist item,
    # not for whole pricelist?..
    price_counter_die = fields.Float("Counter Die Price per sqcm", digits=DP_PRICE)
    mold_of_die_perc = fields.Float("Mold price (% of Die)", digits=DP_PRICE)
    quantity_die_mold_free = fields.Integer(
        "Mold for Free if More than or Equal", help="To disable set to zero."
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.constrains('min_area')
    def _check_min_area(self):
        for rec in self:
            if rec.min_area < 0:
                raise ValidationError(_("Minimum Size must be zero or greater!"))


class StampPricelistItem(models.Model):
    _name = 'stamp.pricelist.item'
    _description = "Stamp Pricelist Item"

    stamp_pricelist_id = fields.Many2one('stamp.pricelist', required=True)
    design_id = fields.Many2one('stamp.design', required=True)
    price = fields.Float(required=True, digits=DP_PRICE)
    company_id = fields.Many2one(related='stamp_pricelist_id.company_id', store=True)
    currency_id = fields.Many2one(related='stamp_pricelist_id.company_id.currency_id')
