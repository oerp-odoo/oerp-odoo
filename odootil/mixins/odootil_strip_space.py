from footil.formatting import strip_space

from odoo import api, models


# IDEA: implement field attribute on string type fields, e.g.
# strip_chars (could set specific chars to strip)
class OdootilStripSpace(models.AbstractModel):
    _name = 'odootil.strip_space'
    _description = "Odootil Strip Whitespaces"

    @property
    def strip_space_fields(self):
        """List of field names to strip spaces from."""
        return []

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._strip_space(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._strip_space(vals)
        return super().write(vals)

    def _strip_space(self, vals):
        for fname in self.strip_space_fields:
            if vals.get(fname):
                vals[fname] = strip_space(vals[fname])
