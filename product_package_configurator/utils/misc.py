from odoo.tools import float_round


def multiply(unit: float, multiplier: float, digits=None):
    val = unit * multiplier
    if digits is not None:
        val = float_round(val, precision_digits=digits)
    return val


def update_by_target(target: int, *numbers: int) -> tuple[int]:
    """Update given given numbers proportionally to have their sum as target."""
    total = sum(numbers)
    ratio = total / target
    res = []
    for n in numbers:
        res.append(int(float_round(n / ratio, precision_digits=0)))
    return tuple(res)
