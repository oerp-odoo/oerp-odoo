from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMassSerialNoComponents(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MO that has some components missing for production.
        cls.mo_1 = cls.env.ref('mrp.mrp_production_1')
        # Make MO product tracked by serial.
        cls.mo_1.product_id.tracking = 'serial'
        cls.picking_type_mo = cls.mo_1.picking_type_id
        cls.mo_1.action_confirm()

    def test_01_mass_produce_open_ignore_missing_components(self):
        # GIVEN
        self.picking_type_mo.mass_serial_ignore_components = True
        # WHEN, THEN
        self.mo_1.action_serial_mass_produce_wizard()

    def test_02_mass_produce_open_not_ignore_missing_components(self):
        # GIVEN
        self.picking_type_mo.mass_serial_ignore_components = False
        # WHEN, THEN
        with self.assertRaisesRegex(
            UserError, r"Make sure enough quantities of these components"
        ):
            self.mo_1.action_serial_mass_produce_wizard()
