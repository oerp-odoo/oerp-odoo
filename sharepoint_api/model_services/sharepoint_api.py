import logging

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.http_client.models.http_client_controller import _raise_endpoint_error

from ..exceptions import MissingSharepointError

_logger = logging.getLogger(__name__)

PFX_SITE = '/v1.0/sites'
PATH_SITE_PATTERN = '{pfx}/{hostname}:{rel_path}'
PATH_DEFAULT_DRIVE_PATTERN = '{pfx}/{site_id}/drive'
PATH_DIR_PATTERN = '{pfx}/{site_id}/drives/{drive_id}/root:{rel_path}'
PATH_DIR_CHILDS_PATTERN = '{pfx}/{site_id}/drives/{drive_id}/root:{rel_path}:/children'


def get_directory_childs_path(site_id: str, drive_id: str, rel_path: str) -> str:
    return PATH_DIR_CHILDS_PATTERN.format(
        pfx=PFX_SITE, site_id=site_id, drive_id=drive_id, rel_path=rel_path
    )


class SharepointApi(models.AbstractModel):
    """Model to communicate with Sharepoint API."""

    _name = 'sharepoint.api'
    _inherit = 'http.client.controller'
    _description = "Sharepoint API"
    _auth_model = 'sharepoint.auth'

    def get_site_id(self, hostname: str, site_rel_path: str, options=None) -> str:
        """Return Sharepoint site ID.

        Args:
            hostname: sharepoint sites hostname
            site_rel_path: relative path of a site (e.g /sites/Mysite)
            options: extra options to propagate (like company_id, auth etc.)

        """
        path = PATH_SITE_PATTERN.format(
            pfx=PFX_SITE, hostname=hostname, rel_path=site_rel_path
        )
        data = self._call_sharepoint_http_method('get', path, options=options).json()
        return data['id']

    def get_default_drive_id(self, site_id: str, options=None) -> str:
        """Get site's default Drive ID.

        It is used to look up documents/folders within.

        Args:
            site_id: sharepoint site ID
            options: extra options

        """
        path = PATH_DEFAULT_DRIVE_PATTERN.format(pfx=PFX_SITE, site_id=site_id)
        data = self._call_sharepoint_http_method('get', path, options=options).json()
        return data['id']

    def get_directory(self, site_id: str, drive_id: str, rel_path: str, options=None):
        """Get information about directory."""
        path = PATH_DIR_PATTERN.format(
            pfx=PFX_SITE, site_id=site_id, drive_id=drive_id, rel_path=rel_path
        )
        return self._call_sharepoint_http_method('get', path, options=options).json()

    def list_directory(
        self, site_id: str, drive_id: str, rel_path: str, options=None
    ) -> dict:
        """Get information about directory childs.

        Args:
            site_id: sharepoint site ID
            drive_id: sharepoint Drive ID
            rel_path: relative path in sharepoint drive
            options: extra options

        """
        path = get_directory_childs_path(site_id, drive_id, rel_path)
        return self._call_sharepoint_http_method('get', path, options=options).json()

    def create_directory(
        self, site_id: str, drive_id: str, rel_path: str, payload: dict, options=None
    ) -> dict:
        """Get information about directory childs.

        Args:
            site_id: sharepoint site ID
            drive_id: sharepoint Drive ID
            rel_path: relative path in sharepoint drive
            payload: data to use to create directory (e.g
                {"name": "MY-NEW-FOLDER", "folder": {}}
            )
            options: extra options

        """
        path = get_directory_childs_path(site_id, drive_id, rel_path)
        return self._call_sharepoint_http_method(
            'post', path, payload=payload, options=options
        ).json()

    def get_expected_exceptions(self):
        res = super().get_expected_exceptions()
        res.append(MissingSharepointError)
        return res

    @api.model
    def postprocess_response_error(self, response):
        """Override to raise exception instead of logging."""
        if response.status_code == 404:
            Exc = MissingSharepointError
        else:
            Exc = ValidationError
        _raise_endpoint_error(response, Exc)

    def _call_sharepoint_http_method(self, verb, path, payload=None, options=None):
        options = self._prepare_request_options(path, payload=payload, options=options)
        # company = self.env['res.company'].browse(options.get('company_id'))
        # self.is_sharepoint_api_enabled(company)
        _logger.debug(
            'Request -> Method: %s. Path: %s. Payload:\n%s',
            verb,
            path,
            payload,
        )
        response = self.call_http_method(verb, options=options)
        _logger.debug(
            'Response -> Method: %s. Path: %s. Status: %s. Response:\n%s',
            verb,
            path,
            response.status_code,
            response.text,
        )
        return response

    def _prepare_request_options(self, path, payload=None, options=None):
        if options is None:
            options = {}
        options.setdefault('kwargs', {})
        if payload is not None:
            options['kwargs']['json'] = payload
        options['uri_item'] = (path, False)
        return options
