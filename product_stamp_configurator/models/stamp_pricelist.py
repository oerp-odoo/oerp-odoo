from odoo import fields, models


class StampPricelist(models.Model):
    _name = 'stamp.pricelist'
    _description = "Stamp Pricelist"

    name = fields.Char(required=True)
    item_ids = fields.One2many(
        'stamp.pricelist.item',
        'stamp_pricelist_id',
        string="Items",
    )
    # TODO: it might make more sense to have these options per pricelist item,
    # not for whole pricelist?..
    price_counter_die = fields.Float("Counter Die Price per sqcm")
    mold_of_die_perc = fields.Float("Mold price (% of Die)")
    quantity_die_mold_free = fields.Integer("Mold for Free if More than or Equal")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')


class StampPricelistItem(models.Model):
    _name = 'stamp.pricelist.item'
    _description = "Stamp Pricelist Item"

    stamp_pricelist_id = fields.Many2one('stamp.pricelist', required=True)
    design_id = fields.Many2one('stamp.design', required=True)
    price = fields.Float(required=True)
    company_id = fields.Many2one(related='stamp_pricelist_id.company_id', store=True)
    currency_id = fields.Many2one(related='stamp_pricelist_id.company_id.currency_id')
