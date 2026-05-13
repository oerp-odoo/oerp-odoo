import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


def _filter_xml_ids(xml_ids, modules=None):
    if not modules:
        return xml_ids
    return [xml_id for xml_id in xml_ids if xml_id.split('.')[0] in modules]


class OdootilToggleActive(models.AbstractModel):
    """Mixin to allow activating/deactivating records."""

    _name = 'odootil.toggle_active'
    _description = 'Odootil Toggle Active'

    @api.model
    def get_xmlids_to_activate(self):
        """Return List of XML IDs to activate.

        Meant to be overridden to add more XML IDs.
        """
        return []

    @api.model
    def get_xmlids_to_deactivate(self):
        """Return List of XML IDs to deactivate.

        Meant to be overridden to add more XML IDs.
        """
        return []

    @api.model
    def _set_active(self, xml_ids, active=True):
        records_map = {}
        for xml_id in xml_ids:
            try:
                record = self.env.ref(xml_id)
                model_name = record._name
                # Group records per their model.
                records_map.setdefault(model_name, self.env[model_name])
                records_map[model_name] |= record
            except ValueError as e:
                _logger.warning(e)
        for records in records_map.values():
            records.write({'active': active})

    @api.model
    def activate(self, enable_filter=None, disable_filter=None):
        """Activate specific records.

        Records in get_xmlids_to_activate, activated, and records in
        get_xmlids_to_deactivate deactivated.

        Can use enabled_filter/disable_filter to enable/disable part
        of records. Useful when need to trigger  on
        installing/uninstalling modules.

        Args:
            enable_filter (list): list of modules to use as filter for
                records to enable.
            disable_filter (list): list of modules to use as filter for
                records to disable.

        """
        xmlids_to_enable = _filter_xml_ids(
            self.get_xmlids_to_activate(), modules=enable_filter
        )
        xmlids_to_disable = _filter_xml_ids(
            self.get_xmlids_to_deactivate(), modules=disable_filter
        )
        self._set_active(xmlids_to_enable, active=True)
        self._set_active(xmlids_to_disable, active=False)

    @api.model
    def deactivate(self, enable_filter=None, disable_filter=None):
        """Deactivate specific records.

        Records in get_xmlids_to_deactivate - activated, and records in
        get_xmlids_to_activate - deactivated.

        Can use enabled_filter/disable_filter to enable/disable part
        of records. Useful when need to trigger  on
        installing/uninstalling modules.

        Args:
            enable_filter (list): list of modules to use as filter for
                records to enable.
            disable_filter (list): list of modules to use as filter for
                records to disable.

        """
        xmlids_to_enable = _filter_xml_ids(
            self.get_xmlids_to_deactivate(), modules=enable_filter
        )
        xmlids_to_disable = _filter_xml_ids(
            self.get_xmlids_to_activate(), modules=disable_filter
        )
        self._set_active(xmlids_to_enable, active=True)
        self._set_active(xmlids_to_disable, active=False)

    @api.model
    def is_enabled(self):
        """Return True if records toggle enabled, False otherwise.

        Must be overridden to implement when access is enabled and
        when is disabled.
        """
        raise NotImplementedError("Toggle Active need to implement 'is_enabled'")
