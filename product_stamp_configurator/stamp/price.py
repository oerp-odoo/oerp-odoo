from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_round

from ..const import DEFAULT_PRICE_DIGITS


def calc_die_price(stamp_cfg, digits=DEFAULT_PRICE_DIGITS):
    material_price = _calc_material_price(stamp_cfg)
    pricelist_price = _calc_pricelist_die_price(stamp_cfg)
    coefficient = stamp_cfg.difficulty_id.coefficient
    if stamp_cfg.design_id.flat_embossed_foiling:
        pricelist_price = _calc_flat_embossed_foiling_price(stamp_cfg, pricelist_price)
    finishing_price = _calc_finishing_price(stamp_cfg)
    price = material_price + pricelist_price * coefficient + finishing_price
    return float_round(price, precision_digits=digits)


def calc_counter_die_price(stamp_cfg, digits=DEFAULT_PRICE_DIGITS):
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    price = stamp_cfg.area_priced * pricelist.price_counter_die
    return float_round(price, precision_digits=digits)


def calc_mold_price(stamp_cfg, digits=DEFAULT_PRICE_DIGITS):
    if _calc_is_mold_free(stamp_cfg):
        return 0.0
    die_price = calc_die_price(stamp_cfg)
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    price = die_price * pricelist.mold_of_die_perc / 100
    return float_round(price, precision_digits=digits)


def calc_price_sqcm_suggested_and_price_unit(
    stamp_cfg, price_unit_suggested, price_sqcm_custom=0, digits=DEFAULT_PRICE_DIGITS
):
    price_sqcm_suggested = convert_price_unit_to_sqcm(
        stamp_cfg, price_unit_suggested, digits=digits
    )
    price_sqcm = price_sqcm_custom or price_sqcm_suggested
    price_unit = convert_price_sqcm_to_unit(stamp_cfg, price_sqcm, digits=digits)
    return (price_sqcm_suggested, price_unit)


def convert_price_unit_to_sqcm(stamp_cfg, price, digits=DEFAULT_PRICE_DIGITS):
    # NOTE. Here using entered area as we are using already calculated
    # price to calculate price per sqm.
    price_per_sqcm = price / stamp_cfg.area
    return float_round(price_per_sqcm, precision_digits=digits)


def convert_price_sqcm_to_unit(stamp_cfg, price_sqcm, digits=DEFAULT_PRICE_DIGITS):
    price_unit = price_sqcm * stamp_cfg.area
    return float_round(price_unit, precision_digits=digits)


def calc_price_sqcm_and_price_unit(
    stamp_cfg, price_sqcm_custom, price_unit_suggested, digits=DEFAULT_PRICE_DIGITS
):
    """Get prices either using custom square cm price or suggested unit price."""
    if price_sqcm_custom:
        price_unit = convert_price_sqcm_to_unit(
            stamp_cfg, price_sqcm_custom, digits=digits
        )
        return (price_sqcm_custom, price_unit)
    price_sqcm = convert_price_unit_to_sqcm(
        stamp_cfg, price_unit_suggested, digits=digits
    )
    return (price_sqcm, price_unit_suggested)


def calc_discount_percent(orig_price, discounted_price):
    if not orig_price:
        return 0
    return 100 * (orig_price - discounted_price) / orig_price


# Die helpers
def _calc_flat_embossed_foiling_price(stamp_cfg, pricelist_price):
    primary_design_price = pricelist_price * stamp_cfg.embossed_design_perc / 100
    base_design_price = _calc_pricelist_die_price(
        stamp_cfg, design=stamp_cfg.design_id.design_base_embossed_id
    )
    return primary_design_price + base_design_price


def _calc_finishing_price(stamp_cfg):
    return stamp_cfg.area_priced * stamp_cfg.finishing_id.price


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


# Mold helpers


def _calc_is_mold_free(stamp_cfg):
    qty = stamp_cfg.quantity_dies_total
    pricelist = stamp_cfg.partner_id.property_stamp_pricelist_id
    qty_free = pricelist.quantity_die_mold_free
    return qty_free and qty >= qty_free
