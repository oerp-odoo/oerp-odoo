from .common import TestBaseCommon


class TestStripSpace(TestBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OdootilTestStripSpace = cls.env['odootil.strip_space.test']

    def test_01_strip_space_on_create(self):
        # WHEN
        rec_1, rec_2 = self.OdootilTestStripSpace.create(
            [
                {'name': 'TES T-\n1', 'code': 'T\r1\t'},
                {'name': 'TEST-2'},
            ]
        )
        # THEN
        self.assertEqual(rec_1.name, 'TEST-1')
        self.assertEqual(rec_1.code, 'T1')
        self.assertEqual(rec_2.name, 'TEST-2')
        self.assertEqual(rec_2.code, False)

    def test_02_strip_space_on_write(self):
        # GIVEN
        rec_1, rec_2 = self.OdootilTestStripSpace.create(
            [
                {'name': 'TEST1', 'code': 'T1'},
                {'name': 'TEST2', 'code': 'T2'},
            ]
        )
        # WHEN
        (rec_1 | rec_2).write({'name': 'TES T-\n1', 'code': False})
        # THEN
        self.assertEqual(rec_1.name, 'TEST-1')
        self.assertEqual(rec_1.code, False)
        self.assertEqual(rec_2.name, 'TEST-1')
        self.assertEqual(rec_2.code, False)
