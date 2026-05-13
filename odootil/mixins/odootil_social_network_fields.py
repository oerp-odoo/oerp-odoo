from odoo import api, fields, models

LINKEDIN_URL = "https://www.linkedin.com/in/%s"
MESSENGER_URL = "https://www.messenger.com/t/%s"


class OdootilSocialNetworkFields(models.AbstractModel):
    """Mixin to include fields of main social networks."""

    _name = 'odootil.social_network.fields'
    _description = "Odootil Social Applications Fields Mixin"

    linkedin_identifier = fields.Char("LinkedIn")
    whatsapp_identifier = fields.Char("WhatsApp")
    skype_identifier = fields.Char("Skype")
    viber_identifier = fields.Char("Viber")
    messenger_identifier = fields.Char("Messenger")

    @api.model
    def prepare_soc_network_acc_act_dict(self, url, identifier):
        """Prepare action to open custom social network account URL."""
        return {
            'type': 'ir.actions.act_url',
            'url': url % identifier,
            'target': 'new',
        }

    def action_open_linkedin_link(self):
        """Open LinkedIn account URL in a new window."""
        self.ensure_one()
        return self.prepare_soc_network_acc_act_dict(
            LINKEDIN_URL, self.linkedin_identifier
        )

    def action_open_messenger_link(self):
        """Open Messenger account URL in a new window."""
        self.ensure_one()
        return self.prepare_soc_network_acc_act_dict(
            MESSENGER_URL, self.messenger_identifier
        )
