from .common import TestOdootilCommon


class TestSetSequence(TestOdootilCommon):
    """Class to test sequence generation and setting its value."""

    @classmethod
    def setUpClass(cls):
        """Set up data for sequence tests."""
        super().setUpClass()
        # Create new company so admin user would not be representing it.
        company = cls.env['res.company'].create({'name': 'T1'})
        cls.company_id = company.id
        cls.seq_1 = cls.env['ir.sequence'].create(
            {'name': 'seq1', 'code': 'custom.seq', 'company_id': False}
        )
        cls.seq_2 = cls.env['ir.sequence'].create(
            {'name': 'seq', 'code': 'custom.seq', 'company_id': cls.company_id}
        )

    def setUp(self):
        """Set up reusable dict."""
        super().setUp()
        self.vals = {}

    def test_01_set_seq(self):
        """Set sequence without company_id.

        Case 1: not force sequence key.
        Case 2: force sequence key.
        """
        # Case 1.
        self.Odootil.set_sequence_number(self.vals, 'number', code='custom.seq')
        self.seq_1.invalidate_recordset()
        self.assertEqual(self.vals['number'], '1')
        self.assertEqual(self.seq_1.number_next_actual, 2)
        self.assertEqual(self.seq_2.number_next_actual, 1)
        # Case 2.
        self.Odootil.set_sequence_number(self.vals, 'number', code='custom.seq')
        # number key already has value so no increment.
        self.assertEqual(self.vals['number'], '1')
        self.assertEqual(self.seq_1.number_next_actual, 2)
        self.assertEqual(self.seq_2.number_next_actual, 1)

    def test_02_set_seq(self):
        """Set sequence with company_id.

        Case 1: use sequence by code.
        Case 2: use sequence by record.
        """
        # NOTE. number_next_actual is not reset between tests, so we
        # must be aware that self.seq_1.number_next_actual == 2.
        # Case 1.
        self.Odootil.set_sequence_number(
            self.vals, 'seq2', code='custom.seq', company_id=self.company_id
        )
        self.seq_2.invalidate_recordset()
        self.assertEqual(self.vals['seq2'], '1')
        self.assertEqual(self.seq_1.number_next_actual, 2)
        self.assertEqual(self.seq_2.number_next_actual, 2)
        # Case 2.
        # If sequence record is passed, company_id is ignored.
        self.Odootil.set_sequence_number(self.vals, 'seq1', sequence=self.seq_1)
        # number key already has value so no increment.
        self.seq_1.invalidate_recordset()
        self.assertEqual(self.vals['seq1'], '2')
        self.assertEqual(self.vals['seq2'], '1')
        self.assertEqual(self.seq_1.number_next_actual, 3)
        self.assertEqual(self.seq_2.number_next_actual, 2)
        # Increment again for seq2.
        del self.vals['seq2']
        self.Odootil.set_sequence_number(self.vals, 'seq2', sequence=self.seq_2)
        self.seq_2.invalidate_recordset()
        self.assertEqual(self.vals['seq1'], '2')
        self.assertEqual(self.vals['seq2'], '2')
        self.assertEqual(self.seq_1.number_next_actual, 3)
        self.assertEqual(self.seq_2.number_next_actual, 3)

    def test_03_set_seq(self):
        """Set non existing sequence."""
        self.Odootil.set_sequence_number(
            self.vals, 'number', code='some.none.existing.sequence'
        )
        self.assertEqual(self.vals['number'], 'New')
        self.Odootil.set_sequence_number(
            self.vals,
            'number2',
            code='some.none.existing.sequence',
            default='Custom',
        )
        self.assertEqual(self.vals['number2'], 'Custom')
