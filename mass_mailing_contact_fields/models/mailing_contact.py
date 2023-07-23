from odoo import api, fields, models


class MailingContact(models.Model):
    """Extend to add extra fields."""

    _inherit = 'mailing.contact'

    state_id = fields.Many2one('res.country.state')
    city = fields.Char()
    # zip is builtin function, so not using it as field name.
    postcode = fields.Char("ZIP")
    phone = fields.Char()

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if (
            self.country_id
            and self.state_id
            and self.state_id not in self.country_id.state_ids
        ):
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id
