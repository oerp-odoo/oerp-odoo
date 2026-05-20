from odoo.exceptions import ValidationError

from . import common


class TestRecordSetHelpers(common.TestOdootilCommon):
    """Class to test recordset helper methods."""

    @classmethod
    def setUpClass(cls):
        """Set up data for recordset helper methods."""
        super().setUpClass()
        cls.ResPartnerCategory = cls.env['res.partner.category']
        cls.partner_1, cls.partner_2, cls.partner_3 = cls.ResPartner.create(
            [
                # color to be used as ordering key.
                {'name': 'MY-PARTNER-1', 'color': 1},
                {'name': 'MY-PARTNER-2', 'color': 2},
                {'name': 'MY-PARTNER-3', 'color': 3},
            ]
        )
        cls.partner_2_child = cls.ResPartner.create(
            {'name': 'MY-PARTNER-2-CHILD-1', 'parent_id': cls.partner_2.id}
        )
        cls.partners = cls.partner_1 | cls.partner_2 | cls.partner_3
        cls.partners_to_sort = cls.partner_1 | cls.partner_3 | cls.partner_2
        cls.partner_4 = cls.ResPartner.create({'name': 'P4'})
        cls._order = 'color, id'
        cls._order_2 = 'color desc, id'
        cls.new_rec_vals = {'name': 'dummy'}
        cls.tag_1, cls.tag_2 = cls.ResPartnerCategory.create(
            [
                {'name': 'MY-TAG-1', 'color': 3},
                {'name': 'MY-TAG-2', 'color': 7},
            ]
        )

    def test_01_get_record_index(self):
        """Get index for partner_1."""
        idx = self.partners.get_record_index(self.partner_1)
        self.assertEqual(idx, 0)
        # Use custom range.
        with self.assertRaises(ValidationError):
            self.partners.get_record_index(self.partner_1, start=1)

    def test_02_get_record_index(self):
        """Get index for partner_3."""
        idx = self.partners.get_record_index(self.partner_3)
        self.assertEqual(idx, 2)
        # Use custom range to not fit in.
        with self.assertRaises(ValidationError):
            self.partners.get_record_index(self.partner_3, start=1, end=2)
        # use custom range to fit in.
        idx = self.partners.get_record_index(self.partner_3, start=2, end=3)
        self.assertEqual(idx, 2)
        # Make start greater than end.
        with self.assertRaises(ValidationError):
            self.partners.get_record_index(self.partner_3, start=4)
        # Use not existing index in recordset.
        with self.assertRaises(IndexError):
            self.partners.get_record_index(self.partner_3, start=4, end=5)

    def test_03_get_record_index(self):
        """Get index for partner_4."""
        with self.assertRaises(ValidationError):
            self.partners.get_record_index(self.partner_4)
        idx = self.partners.get_record_index(self.partner_4, raise_if_not_found=False)
        self.assertEqual(idx, -1)

    def test_04_sorted_virtual(self):
        """Sort only normal recordset."""
        sorted_partners = self.partners_to_sort.sorted_virtual(order_spec=self._order)
        self.assertEqual(sorted_partners, self.partners)

    def test_05_sorted_virtual(self):
        """Sort only NewId recordset."""
        # For some reason, record with NewId (using new method), lose
        # their attribute values, if those are defined on setUpClass. So
        # we define locally inside test method.
        partner_new_4 = self.ResPartner.new({'name': 'new4', 'color': 4})
        partner_new_5 = self.ResPartner.new({'name': 'new5', 'color': 5})
        partners_to_sort = partner_new_5 | partner_new_4
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order)
        self.assertEqual(sorted_partners[0], partner_new_4)
        self.assertEqual(sorted_partners[1], partner_new_5)
        # Make color number the same, so only order records are
        # originally added is used.
        partner_new_5.color = 4
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order)
        self.assertEqual(sorted_partners[0], partner_new_5)
        self.assertEqual(sorted_partners[1], partner_new_4)

    def test_06_sorted_virtual(self):
        """Sort normal records with NewId records."""
        partner_new_4 = self.ResPartner.new({'name': 'new4', 'color': 4})
        partner_new_5 = self.ResPartner.new({'name': 'new5', 'color': 5})
        partners_to_sort = partner_new_5 | partner_new_4 | self.partners_to_sort
        # Sort by color, id.
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order)
        # First three must be normal records.
        self.assertEqual(sorted_partners[:3], self.partners)
        self.assertEqual(sorted_partners[3], partner_new_4)
        self.assertEqual(sorted_partners[4], partner_new_5)
        # Make partner_new_4 color number same as partner_2. It must go
        # after partner_2, because NewId records go after normal
        # records.
        partner_new_4.color = 2
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order)
        self.assertEqual(sorted_partners[:2], self.partner_1 | self.partner_2)
        self.assertEqual(sorted_partners[2], partner_new_4)
        self.assertEqual(sorted_partners[3], self.partner_3)
        self.assertEqual(sorted_partners[4], partner_new_5)
        # Sort only by id.
        sorted_partners = partners_to_sort.sorted_virtual(order_spec='id')
        partners_reversed_by_id = self.partners.sorted(key='id')
        self.assertEqual(sorted_partners[0], partners_reversed_by_id[0])
        self.assertEqual(sorted_partners[1], partners_reversed_by_id[1])
        self.assertEqual(sorted_partners[2], partners_reversed_by_id[2])
        # When sorted by ID, SortedNewId is sorted by position, meaning
        # it will be kept at same position as it was (when comparing two
        # SortedNewId), thus partner_new_5 has index 3 as was
        # originally.
        self.assertEqual(sorted_partners[3], partner_new_5)
        self.assertEqual(sorted_partners[4], partner_new_4)

    def test_07_sorted_virtual(self):
        """Sort normal records with NewId records, with desc option."""
        partner_new_4 = self.ResPartner.new({'name': 'new4', 'color': 4})
        partner_new_5 = self.ResPartner.new({'name': 'new5', 'color': 5})
        partners_reversed = self.partner_3 | self.partner_2 | self.partner_1
        partners_to_sort = partner_new_5 | partner_new_4 | self.partners_to_sort
        # Sort by color, id.
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order_2)
        self.assertEqual(sorted_partners[0], partner_new_5)
        self.assertEqual(sorted_partners[1], partner_new_4)
        self.assertEqual(sorted_partners[2:], partners_reversed)
        # Make partner_new_4 color number same as partner_2. It must
        # before partner_2, because NewId records go after normal
        # records (id is still sorted in ascending order).
        partner_new_4.color = 2
        sorted_partners = partners_to_sort.sorted_virtual(order_spec=self._order_2)
        self.assertEqual(sorted_partners[0], partner_new_5)
        self.assertEqual(sorted_partners[1], self.partner_3)
        self.assertEqual(sorted_partners[2], self.partner_2)
        self.assertEqual(sorted_partners[3], partner_new_4)
        self.assertEqual(sorted_partners[4], self.partner_1)
        # Sort only by id, but in descending order.
        sorted_partners = partners_to_sort.sorted_virtual(order_spec='id DESC')
        self.assertEqual(sorted_partners[0], partner_new_4)
        self.assertEqual(sorted_partners[1], partner_new_5)
        partners_reversed_by_id_desc = self.partners.sorted(key='id', reverse=True)
        self.assertEqual(sorted_partners[2], partners_reversed_by_id_desc[0])
        self.assertEqual(sorted_partners[3], partners_reversed_by_id_desc[1])
        self.assertEqual(sorted_partners[4], partners_reversed_by_id_desc[2])

    def test_08_new_multi(self):
        """Get new record from empty record.

        Case 1: with refs
        Case 2: without refs.
        """
        # Case 1.
        new_rec = self.ResPartner.new_multi(
            values=dict(self.new_rec_vals), refs=['my_ref']
        )
        self.assertEqual(new_rec.name, 'dummy')
        self.assertEqual(new_rec.street, False)
        self.assertEqual(new_rec.id.ref, 'my_ref')
        # Case 2.
        new_rec = self.ResPartner.new_multi(values=dict(self.new_rec_vals))
        self.assertEqual(new_rec.name, 'dummy')
        self.assertEqual(new_rec.street, False)
        self.assertEqual(new_rec.id.ref, None)
        self.assertEqual(new_rec.id.origin, None)

    def test_09_new_multi(self):
        """Get new record from single record (refs passed)."""
        new_rec = self.partner_1.new_multi(
            values=dict(self.new_rec_vals), refs=['my_ref']
        )
        self.assertEqual(new_rec.name, 'dummy')
        self.assertEqual(new_rec.street, self.partner_1.street)
        self.assertEqual(new_rec.id.ref, None)
        self.assertEqual(new_rec.id.origin, self.partner_1.id)

    def test_10_new_multi(self):
        """Get new record from single record (no refs passed)."""
        new_rec = self.partner_1.new_multi(values=dict(self.new_rec_vals))
        self.assertEqual(new_rec.name, 'dummy')
        self.assertEqual(new_rec.street, self.partner_1.street)
        self.assertEqual(new_rec.city, self.partner_1.city)
        self.assertEqual(new_rec.country_id, self.partner_1.country_id)
        self.assertEqual(new_rec.is_company, self.partner_1.is_company)

    def test_11_new_multi(self):
        """Get new records from multiple records."""

        def test_fields(new_rec, partner):
            self.assertEqual(new_rec.name, 'dummy')
            self.assertEqual(new_rec.street, partner.street)
            self.assertEqual(new_rec.street, partner.street)
            self.assertEqual(new_rec.parent_id, partner.parent_id)
            # One2many related records are affected by its parent new,
            # if it has `origin` specified, so these records will also
            # now of NewId instance.
            childs = self.env['res.partner']
            for child in partner.child_ids:
                childs |= self.ResPartner.new(origin=child)
            self.assertEqual(new_rec.child_ids, childs)

        # To make sure it has parent_id.
        child = self.partner_2.child_ids[0]
        recs = (self.partner_1 | child).new_multi(values=dict(self.new_rec_vals))
        self.assertEqual(recs.mapped('name'), ['dummy', 'dummy'])
        rec1, rec2 = (recs[0], recs[1])
        test_fields(rec1, self.partner_1)
        test_fields(rec2, child)

    def test_12_new_multi(self):
        """Get multiple new empty records with ref list."""
        records = self.ResPartner.new_multi(values=dict(self.new_rec_vals), refs=[1, 2])
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].id.ref, 1)
        self.assertEqual(records[1].id.ref, 2)
        self.assertEqual(records[0].id.origin, None)
        self.assertEqual(records[1].id.origin, None)

    def test_13_resolve_2many_commands_to_recs(self):
        """Resolve 2many commands into recs without force create.

        Case 1: 0, 4 commands.
        Case 2: 0, 4, 6 commands.
        Case 3: 0, 4, 5 commands.
        Case 4: 0, 4, 3 commands.
        """
        # Case 1.
        commands = [
            (0, 0, {'name': 'New Tag'}),
            (4, self.tag_1.id),
            (4, self.tag_2.id),
        ]
        tags = self.partner_4.resolve_2many_commands_to_recs('category_id', commands)
        self.assertCountEqual(tags, self.tag_1 | self.tag_2)
        self.assertEqual(
            commands,
            [
                (0, 0, {'name': 'New Tag'}),
                (4, self.tag_1.id),
                (4, self.tag_2.id),
            ],
        )
        # Case 2.
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id',
            [
                (0, 0, {'name': 'New Tag'}),
                (4, self.tag_1.id),
                (6, 0, self.tag_2.ids),
            ],
        )
        self.assertEqual(tags, self.tag_2)
        # Case 3.
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id',
            [(0, 0, {'name': 'New Tag'}), (4, self.tag_1.id), (5,)],
        )
        self.assertFalse(tags)
        # Case 4.
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id',
            [
                (0, 0, {'name': 'New Tag'}),
                (4, self.tag_1.id),
                (3, self.tag_2.id),
            ],
        )
        self.assertEqual(tags, self.tag_1)

    def test_14_resolve_2many_commands_to_recs(self):
        """Resolve 2many commands into recs with force create.

        Case 1: 0, 4 commands.
        Case 2: 0, 4, 6 commands.
        Case 3: 0, 4, 5 commands.
        Case 4: 0, 4, 3 commands.
        """
        # Case 1.
        commands = [
            (0, 0, {'name': 'New Tag 1'}),
            (4, self.tag_1.id),
            (4, self.tag_2.id),
        ]
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id', commands, force_create=True
        )
        tags_prospect_n_services = self.tag_1 | self.tag_2
        tag_new = tags - tags_prospect_n_services
        self.assertEqual(tag_new.name, 'New Tag 1')
        self.assertCountEqual(tags, tags_prospect_n_services | tag_new)
        # Command to create must be removed as we force create it. And
        # new command to reference record must be added.
        self.assertEqual(
            commands,
            [
                (4, self.tag_1.id),
                (4, self.tag_2.id),
                (4, tag_new.id),
            ],
        )
        # Case 2.
        commands = [
            (0, 0, {'name': 'New Tag 2'}),
            (4, self.tag_1.id),
            (6, 0, self.tag_2.ids),
        ]
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id', commands, force_create=True
        )
        # Must not have changed commands.
        self.assertEqual(
            commands,
            [
                (0, 0, {'name': 'New Tag 2'}),
                (4, self.tag_1.id),
                (6, 0, self.tag_2.ids),
            ],
        )
        self.assertEqual(tags, self.tag_2)
        # Case 3.
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id',
            [(0, 0, {'name': 'New Tag 3'}), (4, self.tag_1.id), (5,)],
            force_create=True,
        )
        self.assertFalse(tags)
        # Case 4.
        tags = self.partner_4.resolve_2many_commands_to_recs(
            'category_id',
            [
                (0, 0, {'name': 'New Tag 4'}),
                (4, self.tag_1.id),
                (3, self.tag_2.id),
            ],
            force_create=True,
        )
        tag_new = tags - self.tag_1
        self.assertEqual(tag_new.name, 'New Tag 4')
        self.assertCountEqual(tags, self.tag_1 | tag_new)

    def test_15_sync_related_field_value_from_rel_record(self):
        # GIVEN
        partner_parent = self.ResPartner.create(
            {
                'name': 'MY-PARTNER-1',
                'phone': '+370 699 22456',
                'is_company': True,
            }
        )
        partner_child = self.ResPartner.create(
            {
                'name': 'MY-PARTNER-CHILD-1',
                'parent_id': partner_parent.id,
                'phone': False,
            }
        )
        # WHEN
        partner_child.sync_related_field_value(
            'parent_id',
            'phone',
        )
        # THEN
        self.assertEqual(partner_child.phone, '+370 699 22456')

    def test_16_sync_related_field_value_to_rel_record(self):
        # GIVEN
        partner_parent = self.ResPartner.create(
            {
                'name': 'MY-PARTNER-1',
                'phone': False,
                'is_company': True,
            }
        )
        partner_child = self.ResPartner.create(
            {
                'name': 'MY-PARTNER-CHILD-1',
                'parent_id': partner_parent.id,
                'phone': '+370 699 22456',
            }
        )
        # WHEN
        partner_child.sync_related_field_value('parent_id', 'phone', inverse=True)
        # THEN
        self.assertEqual(partner_parent.phone, '+370 699 22456')
