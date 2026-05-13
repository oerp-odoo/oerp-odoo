from odoo import api, fields, models

DT = fields.Date


class OdootilMonthField(models.AbstractModel):
    """Mixin which adds month field with current month as default."""

    _name = 'odootil.month_field'
    _description = 'Odootil Month Field Mixin'

    @api.model
    def default_get(self, fields):
        """Override to include this month as default odootil_month."""
        res = super().default_get(fields)
        res['odootil_month'] = DT.to_date(DT.context_today(self)).month
        return res

    odootil_month = fields.Selection(
        lambda self: self.env['odootil'].get_months_selection(), "Month"
    )
