from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_round

DIGITS = 2


def calc_die_price(stamp_cfg):
    adjusted_price = _calc_adjusted_price(stamp_cfg)
    return adjusted_price + _calc_finishing_price(stamp_cfg)


def calc_counter_die_price(stamp_cfg):
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    return stamp_cfg.area_priced * pricelist.price_counter_die


def calc_mold_price(stamp_cfg):
    if _calc_is_mold_free(stamp_cfg):
        return 0.0
    die_price = calc_die_price(stamp_cfg)
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    return die_price * pricelist.mold_of_die_perc / 100


def calc_price_per_sqm(stamp_cfg, price, digits=DIGITS):
    # NOTE. Here using entered area as we are using already calculated
    # price to calculate price per sqm.
    price_per_sqm = price / stamp_cfg.area
    return float_round(price_per_sqm, precision_digits=digits)


def calc_discount_percent(orig_price, discounted_price):
    if not orig_price:
        return 0
    return 100 * (orig_price - discounted_price) / orig_price


# Die helpers
def _calc_adjusted_price(stamp_cfg):
    price = _calc_material_price(stamp_cfg)
    if stamp_cfg.design_id.flat_embossed_foiling:
        primary_design_price_adj = (
            _calc_primary_design_price(stamp_cfg) * stamp_cfg.embossed_design_perc / 100
        )
        price += primary_design_price_adj + _calc_embossed_base_design_price(stamp_cfg)
    return price


def _calc_finishing_price(stamp_cfg):
    return stamp_cfg.area_priced * stamp_cfg.finishing_id.price


def _calc_primary_design_price(stamp_cfg):
    price = _calc_pricelist_price_with_difficulty(stamp_cfg)
    return price + _calc_material_price(stamp_cfg)


def _calc_embossed_base_design_price(stamp_cfg):
    return _calc_pricelist_price_with_difficulty(
        stamp_cfg, design=stamp_cfg.design_id.design_base_embossed_id
    )


def _calc_material_price(stamp_cfg):
    return stamp_cfg.area_priced * stamp_cfg.material_id.price


def _calc_pricelist_die_price(stamp_cfg, design=None):
    partner = stamp_cfg.partner_id
    pricelist = partner.property_stamp_pricelist_id
    # TODO: handle when no pricelist is assigned to partner.
    design = design or stamp_cfg.design_id
    for item in pricelist.item_ids:
        if item.design_id == design:
            return stamp_cfg.area_priced * item.price
    raise UserError(
        _(
            "No Stamp Pricelist Price found for Design %(design)s. "
            + "Partner: %(partner)s",
            design=design.name,
            partner=partner.name,
        )
    )


def _calc_pricelist_price_with_difficulty(stamp_cfg, design=None):
    price = _calc_pricelist_die_price(stamp_cfg, design=design)
    return price * stamp_cfg.difficulty_id.coefficient


# Mold helpers


def _calc_is_mold_free(stamp_cfg):
    qty = stamp_cfg.quantity_dies_total
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    qty_free = pricelist.quantity_die_mold_free
    return qty_free and qty >= qty_free
