from .. import const
from . import misc


def calc_area(base_wrapping_area: float, lid_wrapping_area: float):
    """Calculate lamination area in square meters."""
    # TODO: handle shoulder box part as well!
    total_area = base_wrapping_area + lid_wrapping_area
    return total_area * 1.2 / const.MM_TO_SQ_M_COEFFICIENT


def calc_area_and_price(
    base_wrapping_area: float, lid_wrapping_area: float, price_unit: float
) -> dict:
    area = calc_area(base_wrapping_area, lid_wrapping_area)
    price = misc.calc_area_price(price_unit, area)
    return {'area': area, 'price': price}
