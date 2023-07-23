from odoo.tools import float_repr

from .engraving import calc_engraving_time
from .price import DIGITS as PRICE_DIGITS, calc_price_per_sqm

AREA_UOM = 'cm'
PRICE_CM_LABEL = 'eur/cm'
# TODO: use proper UOMs from odoo instead of hardcoding it.
ENGRAVING_UOM = 'val'
# It is calculated with precision 2, but displayed with precision 1.
ENGRAVING_DESCRIPTION_DIGITS = 1


def generate_die_description(
    stamp_cfg,
    price,
    price_digits=PRICE_DIGITS,
    engraving_digits=ENGRAVING_DESCRIPTION_DIGITS,
):
    difficulty_name = stamp_cfg.difficulty_id.name
    area_description = _get_area_description(stamp_cfg)
    price_per_sqm_desc = _get_price_per_scm_description(stamp_cfg, price, price_digits)
    time_description = _get_engraving_time_description(stamp_cfg, engraving_digits)
    return (
        f'{area_description} ; {difficulty_name} ; {price_per_sqm_desc} ; '
        + f'{time_description}'
    )


def _get_area_description(stamp_cfg):
    c = stamp_cfg
    return f'{c.size_length:g}x{c.size_width:g} {AREA_UOM}'


def _get_price_per_scm_description(stamp_cfg, price, digits):
    price_per_sqm = calc_price_per_sqm(stamp_cfg, price, digits=digits)
    price_per_sqm_repr = float_repr(price_per_sqm, precision_digits=digits)
    return f'{price_per_sqm_repr} {PRICE_CM_LABEL}'


def _get_engraving_time_description(stamp_cfg, digits):
    engraving_time = calc_engraving_time(stamp_cfg)
    return f'{engraving_time:.{digits}g} {ENGRAVING_UOM}'
