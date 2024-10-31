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


# TODO: move this to common place!
def get_selection_map(record, fname):
    """Return selection mapping for record field.

    Args:
        record: record to fetch from
        fname (str): selection field name

    Returns:
        selection in map form.
        dict

    """
    return dict(record._fields[fname]._description_selection(record.env))


def get_selection_label(record, fname):
    """Return Label of current selection field value.

    If selection value is falsy, returns empty string. This might
    return unexpected results if one of the selection field values
    is falsy value. It is good practice to specify only truthy
    values for selection values.

    Args:
        record: record to fetch from
        fname (str): selection field name

    Returns:
        str: label of current selection field value.

    """
    val = record[fname]
    if not val:
        return ''
    selection_map = get_selection_map(record, fname)
    return selection_map[val]
