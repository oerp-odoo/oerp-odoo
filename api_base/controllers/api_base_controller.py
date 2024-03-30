from odoo.addons.base_rest.controllers import main

ROOT_PATH = '/api/base/'


class ApiBaseController(main.RestController):
    """Controller class for Base services."""

    _root_path = ROOT_PATH
    _collection_name = 'base.services'
    _default_auth = 'basic'
