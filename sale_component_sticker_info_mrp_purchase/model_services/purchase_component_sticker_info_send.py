from odoo import _, models


class PurchaseComponentStickerInfoSend(models.AbstractModel):
    _name = 'purchase.component.sticker.info.send'
    _description = "Purchase Component Sticker Info Send"

    def send_message(self, purchase):
        partners = self._gather_message_recipients(purchase)
        if not partners:
            return
        return self._send_message(purchase, partners)

    def _gather_message_recipients(self, purchase):
        partner = purchase.partner_id
        partners = partner | partner.child_ids
        return partners.filtered(lambda r: r.components_doc_receiver)

    def _send_message(self, purchase, partners):
        attachment = self._create_sticker_info_attachment(purchase)
        msg_data = self._prepare_message_data(purchase, partners, attachment)
        return purchase.message_post(**msg_data)

    def _prepare_message_data(self, purchase, partners, attachments):
        return {
            'subject': _("Required quantity of components"),
            'body': _("Here is a list of needed components"),
            'partner_ids': partners.ids,
            'attachment_ids': attachments.ids,
        }

    def _create_sticker_info_attachment(self, purchase):
        wiz = self.env['purchase.component.sticker.info.export'].create({})
        data = wiz._generate_csv_base64_data(purchase)
        return self.env['ir.attachment'].create(
            {
                'datas': data,
                'mimetype': 'text/csv',
                'type': 'binary',
                'name': wiz._generate_filename(purchase),
            }
        )
