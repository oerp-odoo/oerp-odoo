from odoo import models, fields


class ResCompany(models.Model):
    """Extend to add field common_note."""

    _inherit = 'res.company'

    common_note = fields.Html(translate=True)

    def interpolate_common_note(self):
        """Use company data to interpolate field common_note."""
        self.ensure_one()
        note = self.common_note
        if not note:
            return ''
        return note.format(company=self)
