from ..tools.record import RecordChangeTracker
from . import common


class TestRecordChangeTracker(common.TestOdootilCommon):
    """Test class for RecordChangeTracker class."""

    @classmethod
    def setUpClass(cls):
        """Set up data for RecordChangeTracker tests."""
        super().setUpClass()
        cls.partners = cls.partner_1 | cls.partner_2 | cls.partner_3 | cls.partner_4
        # To make sure categories won't interfere with tests.
        cls.partners.write({'category_id': [(5,)]})
        cls.partner_category_1 = cls.env.ref('base.res_partner_category_3')
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_ee = cls.env.ref('base.ee')

    def test_01_compute_change(self):
        """Init tracker and change tracked recordset values.

        Fields do not have filtering functions.

        Case 1: nothing changed.
        Case 2: field street changed for all records.
        Case 3: field country_id changed for single record.
        Case 4: field country_id changed for another single record (
            different value)
        Case 5: tracked partner is unlinked.
        Case 6: state saved.
        """
        # Case 1.
        rct = RecordChangeTracker(
            self.partners, ['name', 'street', 'country_id', 'category_id']
        )
        self.assertEqual(rct.compute_change_any(), self.ResPartner)
        self.assertEqual(rct.compute_change_fields(), {})
        self.assertEqual(rct.compute_change_groups(), {})
        self.assertEqual(rct.compute_change_values(), {})
        # Case 2.
        self.partners.write({'street': 'S123'})
        self.assertCountEqual(rct.compute_change_any(), self.partners)
        self.assertCountEqual(rct.compute_change_fields(), {'street': self.partners})
        self.assertCountEqual(
            rct.compute_change_groups(), {frozenset(['street']): self.partners}
        )
        self.assertCountEqual(
            rct.compute_change_values(),
            {
                'street': {
                    'records': self.partners,
                    'by_value': {'S123': self.partners},
                }
            },
        )
        # Case 3.
        self.partner_1.country_id = self.country_lt.id
        self.assertEqual(rct.compute_change_any(), self.partners)
        self.assertEqual(
            rct.compute_change_fields(),
            {'street': self.partners, 'country_id': self.partner_1},
        )
        self.assertCountEqual(
            rct.compute_change_groups(),
            {
                frozenset(['street']): self.partners - self.partner_1,
                frozenset(['street', 'country_id']): self.partner_1,
            },
        )
        self.assertCountEqual(
            rct.compute_change_values(),
            {
                'street': {
                    'records': self.partners,
                    'by_value': {'S123': self.partners},
                },
                'country_id': {
                    'records': self.partner_1,
                    'by_value': {(self.country_lt.id,): self.partner_1},
                },
            },
        )
        # Case 4.
        self.partner_2.country_id = self.country_ee.id
        self.assertCountEqual(rct.compute_change_any(), self.partners)
        self.assertCountEqual(
            rct.compute_change_fields(),
            {
                'street': self.partners,
                'country_id': self.partner_1 | self.partner_2,
            },
        )
        self.assertCountEqual(
            rct.compute_change_groups(),
            {
                frozenset(['street']): (
                    self.partners - self.partner_1 - self.partner_2
                ),
                frozenset(['street', 'country_id']): (self.partner_1 | self.partner_2),
            },
        )
        self.assertCountEqual(
            rct.compute_change_values(),
            {
                'street': {
                    'records': self.partners,
                    'by_value': {'S123': self.partners},
                },
                'country_id': {
                    'records': self.partner_1 | self.partner_2,
                    'by_value': {
                        (self.country_lt.id,): self.partner_1,
                        (self.country_ee.id,): self.partner_2,
                    },
                },
            },
        )
        # Case 5.
        self.partner_2.unlink()
        partners_2 = self.partner_1 | self.partner_3 | self.partner_4
        self.assertEqual(rct.compute_change_any(), partners_2)
        self.assertCountEqual(
            rct.compute_change_fields(),
            {'street': partners_2, 'country_id': self.partner_1},
        )
        self.assertCountEqual(
            rct.compute_change_groups(),
            {
                frozenset(['street']): self.partners - self.partner_1,
                frozenset(['street', 'country_id']): self.partner_1,
            },
        )
        self.assertCountEqual(
            rct.compute_change_values(),
            {
                'street': {
                    'records': partners_2,
                    'by_value': {'S123': partners_2},
                },
                'country_id': {
                    'records': self.partner_1,
                    'by_value': {
                        (self.country_lt.id,): self.partner_1,
                    },
                },
            },
        )
        # Case 6.
        rct.save()
        self.assertEqual(rct.compute_change_any(), self.ResPartner)
        self.assertEqual(rct.compute_change_fields(), {})
        self.assertEqual(rct.compute_change_groups(), {})
        self.assertEqual(rct.compute_change_values(), {})

    def test_02_compute_change(self):
        """Init tracker and change tracked recordset values.

        Some fields have filtering functions.

        Case 1: nothing changed.
        Case 2: field street changes for two records. One change is
            ignored by filter, another not ignored.
        Case 3: field country_id changed for all records. Filter ignores
            change for all records.
        Case 4: field category_id changes for all records, filter passed
            for all records.
        Case 5: partner_4 street changed to STREET1
        """
        # Case 1.
        rct = RecordChangeTracker(
            self.partners,
            [
                'name',
                ('street', lambda r: r.street == 'STREET1'),
                ('country_id', lambda r: r.country_id.code == 'LT'),
                (
                    'category_id',
                    lambda r: self.partner_category_1 in r.category_id,
                ),
            ],
        )
        self.assertEqual(rct.compute_change_values(), {})
        # Case 2.
        self.partner_1.street = 'STREET1'
        self.partner_2.street = 'STREET2'
        changes = {
            'street': {
                'records': self.partner_1,
                'by_value': {'STREET1': self.partner_1},
            }
        }
        self.assertCountEqual(rct.compute_change_values(), changes)
        # Case 3.
        self.partners.write({'country_id': self.country_ee.id})
        # Nothing should have changed.
        self.assertCountEqual(rct.compute_change_values(), changes)
        # Case 4.
        self.partners.write({'category_id': [(4, self.partner_category_1.id)]})
        changes['category_id'] = {
            'records': self.partners,
            'by_value': {(self.partner_category_1.id,): self.partners},
        }
        self.assertCountEqual(rct.compute_change_values(), changes)
        # Case 5.
        self.partner_4.street = 'STREET1'
        self.assertCountEqual(
            rct.compute_change_groups(),
            {
                frozenset(['category_id']): self.partner_2 | self.partner_3,
                frozenset(['street', 'category_id']): (self.partner_1 | self.partner_4),
            },
        )
        changes['street']['records'] |= self.partner_4
        changes['street']['by_value']['STREET1'] |= self.partner_4
        self.assertCountEqual(rct.compute_change_values(), changes)

    def test_03_compute_change(self):
        """Use tracker when records are changed but not register change.

        Case 1: unrelated field changed.
        Case 2: tracked field changed to same value.
        """
        # Case 1.
        rct = RecordChangeTracker(
            self.partners, ['street', 'country_id', 'category_id']
        )
        self.partners.write({'name': 'Dummy Name'})
        self.assertEqual(rct.compute_change_values(), {})
        # Case 2.
        self.partner_1.street = self.partner_1.street
        self.assertEqual(rct.compute_change_values(), {})
