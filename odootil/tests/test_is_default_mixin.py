from odoo.exceptions import ValidationError

from .common import TestBaseCommon


class TestIsDefaultMixin(TestBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OdootilIsDefaultTestSingle = cls.env['odootil.is_default.test.single']
        cls.OdootilIsDefaultTestSingleMultiCompany = cls.env[
            'odootil.is_default.test.single.multicompany'
        ]
        cls.OdootilIsDefaultTestMulti = cls.env['odootil.is_default.test.multi']
        cls.test_single_1 = cls.OdootilIsDefaultTestSingle.create(
            {'name': 'MY-TEST-SINGLE-1', 'is_default': True}
        )
        (cls.test_single_multicompany_1) = (
            cls.OdootilIsDefaultTestSingleMultiCompany.create(
                {
                    'name': 'MY-TEST-SINGLE-MULTICOMPANY-1',
                    'is_default': True,
                    'company_id': cls.company_main.id,
                }
            )
        )
        cls.test_multi_1 = cls.OdootilIsDefaultTestMulti.create(
            {'name': 'MY-TEST-MULTI-1', 'is_default': True}
        )

    def test_01_is_default_get_single(self):
        self.assertEqual(
            self.OdootilIsDefaultTestSingle.is_default_get(), self.test_single_1
        )

    def test_02_is_default_get_single_no_match(self):
        # GIVEN
        self.test_single_1.is_default = False
        # WHEN, THEN
        self.assertFalse(self.OdootilIsDefaultTestSingle.is_default_get())

    def test_03_is_default_get_single_multicompany_match(self):
        self.assertEqual(
            self.OdootilIsDefaultTestSingleMultiCompany.is_default_get(
                company_id=self.company_main.id
            ),
            self.test_single_multicompany_1,
        )

    def test_04_is_default_get_single_multicompany_not_match(self):
        # GIVEN
        self.assertFalse(
            self.OdootilIsDefaultTestSingleMultiCompany.is_default_get(
                # To not find any.
                company_id=0
            ),
        )

    def test_05_is_default_get_single_multicompany_missing_company_id_in_kw(self):
        # GIVEN
        with self.assertRaisesRegex(ValidationError, r"Programming error:"):
            self.OdootilIsDefaultTestSingleMultiCompany.is_default_get(),

    def test_06_is_default_single_not_unique(self):
        with self.assertRaisesRegex(
            ValidationError,
            r"Only single 'Odootil Is Default Test Single' can be default!",
        ):
            self.OdootilIsDefaultTestSingle.create(
                {'name': 'MY-TEST-SINGLE-2', 'is_default': True}
            )

    def test_07_is_default_single_unique(self):
        try:
            self.OdootilIsDefaultTestSingle.create(
                {
                    'name': 'MY-TEST-SINGLE-2',
                    'is_default': False,
                }
            )
        except ValidationError as e:
            self.fail(f"New record has is_default=False, so must pass. Error: {e}")

    def test_08_is_default_single_multicompany_not_unique(self):
        with self.assertRaisesRegex(
            ValidationError,
            r"Only single 'Odootil Is Default Test Single Multi-Company' can be "
            + "default per company!",
        ):
            self.OdootilIsDefaultTestSingleMultiCompany.create(
                {
                    'name': 'MY-TEST-SINGLE-MULTICOMPANY-2',
                    'is_default': True,
                    'company_id': self.company_main.id,
                }
            )

    def test_09_is_default_single_multicompany_unique(self):
        # GIVEN
        company = self.ResCompany.create({'name': 'MY-COMPANY-2222'})
        try:
            self.OdootilIsDefaultTestSingleMultiCompany.create(
                {
                    'name': 'MY-TEST-SINGLE-MULTICOMPANY-2',
                    'is_default': True,
                    'company_id': company.id,
                }
            )
        except ValidationError as e:
            self.fail(f"Different company used, so must pass. Error: {e}")

    def test_10_is_default_multi_no_constraint(self):
        try:
            self.OdootilIsDefaultTestMulti.create(
                {
                    'name': 'MY-TEST-MULTI-2',
                    'is_default': True,
                }
            )
        except ValidationError as e:
            self.fail(f"Multi default allows multiple defaults. Error: {e}")

    def test_11_check_is_default_single_deps(self):
        self.assertEqual(
            self.OdootilIsDefaultTestSingle.is_default_prepare_check_deps(),
            ['is_default'],
        )

    def test_12_check_is_default_single_multicompany_active_deps(self):
        self.assertEqual(
            self.OdootilIsDefaultTestSingleMultiCompany.is_default_prepare_check_deps(),
            ['is_default', 'company_id', 'active'],
        )
