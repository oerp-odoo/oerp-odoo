from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_repr

from ..const import DP_PRICE


class StampPricelist(models.Model):
    _name = 'stamp.pricelist'
    _inherit = 'mail.thread'
    _description = "Stamp Pricelist"

    name = fields.Char(required=True, tracking=True)
    item_ids = fields.One2many(
        'stamp.pricelist.item',
        'stamp_pricelist_id',
        string="Items",
    )
    # Area term makes more sense here, but keeping Size in label as its
    # more familiar to users.
    min_area = fields.Float(
        "Minimum Size, cm2",
        tracking=True,
        help="Will use this size to calculate price if entered size in "
        + "configurator is lower than this. Keep 0 to not use it.",
    )
    # TODO: it might make more sense to have these options per pricelist item,
    # not for whole pricelist?..
    price_counter_die = fields.Float(
        "Counter Die Price per sqcm",
        digits=DP_PRICE,
        tracking=True,
    )
    mold_of_die_perc = fields.Float(
        "Mold price (% of Die)", digits=DP_PRICE, tracking=True
    )
    quantity_die_mold_free = fields.Integer(
        "Mold for Free if More than or Equal",
        help="To disable set to zero.",
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company, tracking=True
    )
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.constrains('min_area')
    def _check_min_area(self):
        for rec in self:
            if rec.min_area < 0:
                raise ValidationError(_("Minimum Size must be zero or greater!"))


class StampPricelistItem(models.Model):
    _name = 'stamp.pricelist.item'
    _inherit = 'mail.thread'
    _description = "Stamp Pricelist Item"

    name = fields.Char(compute='_compute_name')
    stamp_pricelist_id = fields.Many2one(
        'stamp.pricelist', required=True, tracking=True
    )
    design_id = fields.Many2one('stamp.design', required=True, tracking=True)
    price = fields.Float(required=True, digits=DP_PRICE, tracking=True)
    company_id = fields.Many2one(related='stamp_pricelist_id.company_id', store=True)
    currency_id = fields.Many2one(related='stamp_pricelist_id.company_id.currency_id')

    @api.depends('design_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.design_id:
                rec.name = f'[{rec.id}] {rec.design_id.name}'
            else:
                rec.name = False

    def action_open_item(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product_stamp_configurator.stamp_pricelist_item_action"
        )
        action.update(
            {
                "view_mode": "form",
                "views": False,
                "view_id": False,
                "res_id": self.id,
            }
        )
        return action

    def unlink(self):
        self._post_unlink_messages()
        return super().unlink()

    def _post_unlink_messages(self):
        groups = defaultdict(lambda: self.env[self._name])
        for item in self:
            groups[item.stamp_pricelist_id] |= item
        for pricelist, items in groups.items():
            body = items._prepare_unlink_message()
            pricelist.message_post(body=body, message_type='notification')

    def _prepare_unlink_message(self):
        digits = self.env['decimal.precision'].precision_get(DP_PRICE)
        body = 'Items were deleted:'
        for item in self:
            price = float_repr(item.price, precision_digits=digits)
            body += f'<br>* name: {item.display_name}, price: {price}<br>'
        return body
