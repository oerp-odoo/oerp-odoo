from odoo.addons.component.core import AbstractComponent

from ..apispec.basic_security_plugin import BasicSecurityPlugin


class BaseRestService(AbstractComponent):
    _inherit = 'base.rest.service'

    def _get_api_spec(self, **params):
        spec = super()._get_api_spec(**params)
        plugin = BasicSecurityPlugin(self)
        plugin.init_spec(spec)
        spec.plugins.append(plugin)
        return spec
