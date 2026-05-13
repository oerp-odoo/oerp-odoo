from ast import literal_eval

from odoo import api, models


class IrConfigParameter(models.Model):
    """Extend to add config parameter helpers."""

    _inherit = 'ir.config_parameter'

    @api.model
    def get_param_eval(self, key, default=False, eval_fun=literal_eval):
        """Retrieve the value for a given key and convert it.

        Value is retrieved using `get_param` method. If eval_fun is
        provided, value is then converted using that function. Otherwise
        no conversion is done.

        Args:
            key (str): The key of the parameter value to retrieve.
            default: default value if parameter is missing (
                default: {False}).
            eval_fun: function to convert retrieved value (default:
                {literal_eval}).

        Returns:
            type converted using eval_fun or str if no conversion done,
            or default value if nothing was found (last option works
            the same as `get_param` method).

        """
        value = self.get_param(key, default=default)
        # Check if we actually got param. If value matches with default,
        # it means we did not found param and it returned default value.
        if value == default:
            return default
        return eval_fun(value)
