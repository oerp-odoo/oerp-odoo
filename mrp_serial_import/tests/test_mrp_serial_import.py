import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


SERIAL_NUMBERS_A = b"""name,ref,note
SN001,A1,
SN002,A2,Special Serial
SN003,A3,"""

SERIAL_NUMBERS_B = b"""name
SN001
SN002
SN003"""

SERIAL_NUMBERS_C = b"""not_existing_column
SN001
SN002
SN003"""


class TestMrpSerialImport(TransactionCase):
    """Class to test manufactured products serial numbers import."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.MrpProduction = cls.env['mrp.production']
        cls.StockAssignSerial = cls.env['stock.assign.serial']
        cls.product_lodge = cls.env.ref(
            'mrp_serial_import.product_product_lodge'
        )
        cls.bom_lodge = cls.env.ref('mrp_serial_import.mrp_bom_lodge')
        cls.bom_lodge_line = cls.env.ref('mrp_serial_import.mrp_bom_line_1')
        cls.production_lodge = cls.MrpProduction.create({
            'product_id': cls.product_lodge.id,
            'product_qty': 3,
            'bom_id': cls.bom_lodge.id,
            'product_uom_id': cls.product_lodge.uom_id.id,
        })
        cls.production_lodge.action_confirm()

    def _map_lots_by_name(self, production):
        productions = production.procurement_group_id.mrp_production_ids
        return dict(
            productions.mapped(
                lambda r: (r.lot_producing_id.name, r.lot_producing_id)
            )
        )

    def test_01_assign_serial(self):
        """Mass assign serial numbers via file (with extra data)."""
        action = self.production_lodge.action_serial_mass_produce_wizard()
        wizard = self.StockAssignSerial.with_context(
            **action['context']
        ).create({'next_serial_number': 'Placeholder'})
        self.assertEqual(wizard.next_serial_number, 'Placeholder')
        wizard.serial_numbers_file = base64.b64encode(SERIAL_NUMBERS_A)
        wizard._onchange_serial_numbers_file()
        self.assertEqual(wizard.next_serial_number, 'SN001')
        self.assertEqual(
            wizard.serial_numbers_file_data,
            {
                'SN001': {'ref': 'A1', 'note': False},
                'SN002': {'ref': 'A2', 'note': 'Special Serial'},
                'SN003': {'ref': 'A3', 'note': False}
            },
        )
        self.assertEqual(wizard.serial_numbers, 'SN001\nSN002\nSN003')
        wizard._onchange_serial_numbers()
        self.assertEqual(wizard.produced_qty, 3)
        wizard.apply()
        lots_map = self._map_lots_by_name(self.production_lodge)
        self.assertEqual(lots_map['SN001']['ref'], 'A1')
        self.assertEqual(lots_map['SN001']['note'], False)
        self.assertEqual(lots_map['SN002']['ref'], 'A2')
        self.assertEqual(
            str(lots_map['SN002']['note']), '<p>Special Serial</p>'
        )
        self.assertEqual(lots_map['SN003']['ref'], 'A3')
        self.assertEqual(lots_map['SN003']['note'], False)

    def test_02_assign_serial(self):
        """Mass assign serial numbers via file (no extra data)."""
        action = self.production_lodge.action_serial_mass_produce_wizard()
        wizard = self.StockAssignSerial.with_context(
            **action['context']
        ).create({'next_serial_number': 'Placeholder'})
        self.assertEqual(wizard.next_serial_number, 'Placeholder')
        wizard.serial_numbers_file = base64.b64encode(SERIAL_NUMBERS_B)
        wizard._onchange_serial_numbers_file()
        self.assertEqual(wizard.next_serial_number, 'SN001')
        self.assertEqual(
            wizard.serial_numbers_file_data,
            {'SN001': {}, 'SN002': {}, 'SN003': {}},
        )
        self.assertEqual(wizard.serial_numbers, 'SN001\nSN002\nSN003')
        wizard._onchange_serial_numbers()
        self.assertEqual(wizard.produced_qty, 3)
        wizard.apply()
        lots_map = self._map_lots_by_name(self.production_lodge)
        self.assertEqual(lots_map['SN001']['ref'], False)
        self.assertEqual(lots_map['SN001']['note'], False)
        self.assertEqual(lots_map['SN002']['ref'], False)
        self.assertEqual(lots_map['SN002']['note'], False)
        self.assertEqual(lots_map['SN003']['ref'], False)
        self.assertEqual(lots_map['SN003']['note'], False)

    def test_03_assign_serial(self):
        """Try to assign serial numbers with file missing name col."""
        action = self.production_lodge.action_serial_mass_produce_wizard()
        wizard = self.StockAssignSerial.with_context(
            **action['context']
        ).create({'next_serial_number': 'Placeholder'})
        self.assertEqual(wizard.next_serial_number, 'Placeholder')
        wizard.serial_numbers_file = base64.b64encode(SERIAL_NUMBERS_C)
        with self.assertRaises(UserError):
            wizard._onchange_serial_numbers_file()
