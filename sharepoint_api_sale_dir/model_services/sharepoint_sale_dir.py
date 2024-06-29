from odoo import models

from odoo.addons.sharepoint_api.exceptions import MissingSharepointError


class SharepointSaleDir(models.AbstractModel):
    _name = 'sharepoint.sale.dir'
    _description = "Sharepoint Sale Directory Service"

    def retrieve_web_url(self, sale):
        """Retrieve directory URL related to sale order.

        If directory does not exist, it will be created.
        """
        site = self.env['sharepoint.site'].get_site(
            sale.company_id, raise_not_found=True, sale_dir=True
        )
        options = {'auth': site.auth_id}
        SharepointApi = self.env['sharepoint.api']
        try:
            dir_data = self.env['sharepoint.api'].get_directory(
                site.site_id,
                site.drive_id,
                self._generate_sale_dir_rel_path(sale, site),
                options=options,
            )
            return dir_data['webUrl']
        except MissingSharepointError:
            res = SharepointApi.create_directory(
                site.site_id,
                site.drive_id,
                self._generate_sale_dir_parent_rel_path(sale, site),
                payload={"name": sale.name, "folder": {}},
                options=options,
            )
            return res['webUrl']

    def _generate_sale_dir_parent_rel_path(self, sale, site):
        pname = sale.partner_id.commercial_partner_id.name
        return f'{site.sale_dir_root_path}/{pname}'

    def _generate_sale_dir_rel_path(self, sale, site):
        parent_path = self._generate_sale_dir_parent_rel_path(sale, site)
        return f'{parent_path}/{sale.name}'
