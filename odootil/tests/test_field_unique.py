from odoo.exceptions import ValidationError

from ..tools.validation import check_field_unique
from .common import TestBaseCommon


class TestFieldUnique(TestBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OdootilTestFieldUnique = cls.env['odootil.test.field.unique']
        cls.OdootilTestFieldUniqueMultiCompany = cls.env[
            'odootil.test.field.unique.multicompany'
        ]

    def test_01_check_field_unique_case_insensitive_ok(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1'},
                {'name': 'TEST-2', 'code': 'T2'},
            ]
        )
        # WHEN, THEN
        try:
            res = check_field_unique(recs, 'code', case_insensitive=True)
        except ValidationError as e:
            self.fail(f"Should not fail - codes are unique. Error: {e}")
        self.assertTrue(res)

    def test_02_check_field_unique_case_insensitive_raise_fail(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1'},
                {'name': 'TEST-2', 'code': 't1'},
            ]
        )
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Code 'T1' must be unique\!"):
            check_field_unique(recs, 'code', case_insensitive=True)

    def test_03_check_field_unique_case_insensitive_no_raise_fail(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1'},
                {'name': 'TEST-2', 'code': 't1'},
            ]
        )
        # WHEN, THEN
        try:
            res = check_field_unique(
                recs, 'code', case_insensitive=True, raise_exc=False
            )
        except ValidationError as e:
            self.fail(f"Should not raise, raise exception is muted. Error: {e}")
        self.assertFalse(res)

    def test_04_check_field_unique_case_sensitive_ok(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1'},
                {'name': 'TEST-2', 'code': 't1'},
            ]
        )
        # WHEN, THEN
        try:
            res = check_field_unique(recs, 'code', case_insensitive=False)
        except ValidationError as e:
            self.fail(f"Should not fail, codes are unique. Error: {e}")
        self.assertTrue(res)

    def test_05_check_field_unique_case_sensitive_raise_fail(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1'},
                {'name': 'TEST-2', 'code': 'T1'},
            ]
        )
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Code 'T1' must be unique\!"):
            check_field_unique(recs, 'code', case_insensitive=False)

    def test_06_check_boolean_truthy_field_not_unique(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1', 'is_default': True},
                {'name': 'TEST-2', 'code': 'T2', 'is_default': True},
            ]
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Is Default 'True' must be unique!"
        ):
            check_field_unique(recs, 'is_default')

    def test_07_check_boolean_truthy_field_considered_unique(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1', 'is_default': False},
                {'name': 'TEST-2', 'code': 'T2', 'is_default': False},
            ]
        )
        # WHEN, THEN
        try:
            check_field_unique(recs, 'is_default', predicate=lambda r: r.is_default)
        except ValidationError as e:
            self.fail(f"Must be considered unique. Error: {e}")

    def test_08_check_boolean_truthy_field_unique(self):
        # GIVEN
        recs = self.OdootilTestFieldUnique.create(
            [
                {'name': 'TEST-1', 'code': 'T1', 'is_default': True},
                {'name': 'TEST-2', 'code': 'T2', 'is_default': False},
            ]
        )
        # WHEN, THEN
        try:
            check_field_unique(recs, 'is_default')
        except ValidationError as e:
            self.fail(f"Must be unique. Error: {e}")

    def test_09_check_code_unique_multi_company_ok(self):
        # GIVEN
        company = self.ResCompany.create({'name': 'TEST-1'})
        self.OdootilTestFieldUniqueMultiCompany.create({'name': 'TEST-1', 'code': 'T1'})
        # WHEN, THEN
        try:
            self.OdootilTestFieldUniqueMultiCompany.create(
                {'name': 'TEST-1', 'code': 'T1', 'company_id': company.id}
            )
        except ValidationError as e:
            self.fail(f"Should not fail - code is unique. Error: {e}")

    def test_10_check_code_unique_multi_company_fail_active(self):
        # GIVEN
        self.OdootilTestFieldUniqueMultiCompany.create({'name': 'TEST-1', 'code': 'T1'})
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Code 'T1' must be unique\!"):
            self.OdootilTestFieldUniqueMultiCompany.create(
                {'name': 'TEST-1', 'code': 'T1'}
            )

    def test_11_check_code_unique_multi_company_fail_archived(self):
        # GIVEN
        self.OdootilTestFieldUniqueMultiCompany.create(
            {'name': 'TEST-1', 'code': 'T1', 'active': False}
        )
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Code 'T1' must be unique\!"):
            self.OdootilTestFieldUniqueMultiCompany.create(
                {'name': 'TEST-1', 'code': 'T1'}
            )
