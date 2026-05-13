from odoo.tools.misc import frozendict


def deep_freeze_dict(d: dict) -> frozendict:
    """Make nested dictionary immutable."""
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = deep_freeze_dict(v)
    return frozendict(d)
