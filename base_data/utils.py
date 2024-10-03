import ast

from odoo import _
from odoo.exceptions import ValidationError


def validate_dict_str(data, msg):
    try:
        defaults = ast.literal_eval(data)
        if not isinstance(defaults, dict):
            raise ValidationError(msg)
    except Exception as e:
        # FIXME: this will not translate as odoo can only translate from odoo model
        # methods..
        raise ValidationError(msg + _(" Error: %s", e))
