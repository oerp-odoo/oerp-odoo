from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sharepoint_sale_dir_url = fields.Char("Sharepoint Directory URL")

    def action_open_sharepoint_directory(self):
        self.ensure_one()
        res = {
            'type': 'ir.actions.act_url',
            'target': 'new',
        }
        url = self.sharepoint_sale_dir_url
        if not url:
            url = self.env['sharepoint.sale.dir'].sudo().retrieve_web_url(self)
            self.sharepoint_sale_dir_url = url
        res['url'] = url
        return res
