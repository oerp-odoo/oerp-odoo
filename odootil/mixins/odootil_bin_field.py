from odoo import models


class OdootilBinField(models.AbstractModel):
    """Mixin model meant to be inherited by other models.

    It can be used for downloading binary data directly from binary field,
    e.g. use to download custom data file from wizard.

    Configurable attributes which must be defined on target class:

    `_odootil_bin_field_datas`, e.g.:
        `datas = fields.Binary('File', readonly=True)`.

    `_odootil_bin_field_filename`, e.g.:
        `datas_fname = fields.Char(string='Filename', size=256, readonly=True)`
    """

    _name = 'odootil.bin_field'
    _description = 'Odootil Binary Field Mixin'
    _odootil_bin_field_datas = 'datas'
    _odootil_bin_field_filename = 'store_fname'

    def odootil_bin_field_download(self, field=None, filename=None, target='self'):
        """Download file from binary field."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content?model=%s&id=%s&field=%s&filename_field=%s&"
            "download=true"
            % (
                self._name,
                self.id,
                field or self._odootil_bin_field_datas,
                filename or self._odootil_bin_field_filename,
            ),
            'target': target,
        }
