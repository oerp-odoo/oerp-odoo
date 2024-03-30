from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.extendable.tests.common import ExtendableMixin


class TestApiBaseCommon(BaseRestCase, ExtendableMixin):
    """Common class for Base API tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for Base API tests."""
        super().setUpClass()
        cls.setUpExtendable()
        collection = _PseudoCollection("base.services", cls.env)
        cls.base_services_env = WorkContext(
            model_name="rest.service.registration", collection=collection
        )
        cls.ResPartner = cls.env['res.partner']
        cls.company_main = cls.env.ref('base.main_company')
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_us = cls.env.ref('base.us')

    # Using this as there is an issue with the way ExtendableMixin
    # is implemented (see base_rest_demo.tests.common).
    def setUp(self):
        BaseRestCase.setUp(self)
        ExtendableMixin.setUp(self)
