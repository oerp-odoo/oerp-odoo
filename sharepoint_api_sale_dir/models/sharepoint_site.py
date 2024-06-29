from odoo import fields, models


class Share(models.Model):
    _inherit = 'sharepoint.site'

    # Sale Documents Root Path
    sale_dir_root_path = fields.Char(
        "Sale Directories Root Path",
        help="Used to create/link sale orders with Sharepoint directories",
    )

    def prepare_site_domain(self, company, **kw):
        domain = super().prepare_site_domain(company, **kw)
        if kw.get('sale_dir'):
            domain.append(('sale_dir_root_path', '!=', False))
        return domain
